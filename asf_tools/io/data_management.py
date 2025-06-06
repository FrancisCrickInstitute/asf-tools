"""
Helper functions for data management
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from enum import Enum

from asf_tools.io.utils import DeleteMode, check_file_exist, delete_all_items
from asf_tools.slurm.utils import get_job_status


# Set up logging as the root logger
log = logging.getLogger()


class DataTypeMode(Enum):
    """
    - GENERAL: General mode, applicable for all sequencing types.
    - ONT: Oxford Nanopore Technology (ONT) sequencing data.
    - ILLUMINA: Illumina sequencing data.
    """

    GENERAL = "general"
    ONT = "ont"
    ILLUMINA = "illumina"


class DataManagement:
    """
    Helper functions for data management
    """

    def __init__(self, storage_interface):
        self.storage_interface = storage_interface

    def check_pipeline_run_complete(self, run_dir: str):
        """
        Check if a pipeline run directory is complete by checking for the presence of the `workflow_complete` file.

        Args:
        - run_dir (str): Path to the run directory.

        Returns:
        - bool: True if the run directory is complete, False otherwise.
        """
        completed_file = os.path.join(run_dir, "results", "pipeline_info", "workflow_complete.txt")
        return self.storage_interface.exists(completed_file)

    def check_ont_sequencing_run_complete(self, run_dir: str):
        """
        Check if an ONT sequencing run is complete by checking for the presence of the `sequencing_summary`
        file.

        Args:
        - run_dir (str): Path to the run directory.
        """
        return self.storage_interface.exists_with_pattern(run_dir, "sequencing_summary*")

        # check for pod5 count file
        # if not check_file_exist(run_dir, "pod5_count.txt"):
        #     return False

        # # read single integer from pod5_count.txt
        # pod5_expected_max = -1
        # with open(os.path.join(run_dir, "pod5_count.txt"), "r", encoding="UTF-8") as f:
        #     file_contents = f.readline().strip()
        #     if file_contents.isdigit():
        #         pod5_expected_max = int(file_contents)
        #         log.debug(f"{run_dir} - pod5_expected_max: {pod5_expected_max}")

        # # find all the pod5 files in any subdirectory of the run_dir and get max
        # pod5_numbers = [0]
        # for root, dirs, files in os.walk(run_dir):  # pylint: disable=unused-variable
        #     for file in files:
        #         if file.endswith(".pod5"):
        #             match = re.search(r"_(\d+)\.pod5", file)
        #             if match:
        #                 pod5_numbers.append(int(match.group(1)))
        # pod5_max = max(pod5_numbers)
        # log.debug(f"{run_dir} - pod5_max: {pod5_expected_max}")

        # return pod5_max == pod5_expected_max
        # return True

    def check_illumina_sequencing_run_complete(self, run_dir: str):
        """
        Check if an Illumina run has completed data transfer by checking for the presence of the
        `RTAcomplete`, `RunCompletionStatus` and `CopyComplete` files.

        Args:
        - run_dir (str): Path to the run directory.

        Returns:
        - bool: True if the run directory is complete, False otherwise.
        """
        completed_files = ["RTAComplete.txt", "RunCompletionStatus.xml", "CopyComplete.txt"]
        # file_exists = all(check_file_exist(run_dir, file) for file in completed_files)
        file_exists = all(self.storage_interface.exists(os.path.join(run_dir, file)) for file in completed_files)

        if file_exists:
            completed_file = os.path.join(run_dir, "RunCompletionStatus.xml")
            with open(completed_file, "r", encoding="utf-8") as file:
                contents = file.read()

                # Check if "RunCompleted" exists in the file content
                if "RunCompleted" in contents:
                    return True
        return False

    def symlink_to_target(self, data_path: str, symlink_data_path):
        """
        Creates symbolic links for a given data path in one or multiple destination paths.

        Args:
        - data_path (str): Path to the source data to be symlinked.
        - symlink_data_path (Union[str, list]): Single path or list of paths where the symlinks should be created.

        Raises:
        - ValueError: If symlink_data_path is neither a string nor a list.

        Example usage:
        symlink_to_target('/path/to/source', '/path/to/destination')
        symlink_to_target('/path/to/source', ['/path/to/dest1', '/path/to/dest2'])
        """

        # Check if source paths exists - commented out as I need to be able to symlink to non-existent paths
        # if not os.path.exists(data_path):
        #     raise FileNotFoundError(f"{data_path} does not exist.")

        # Check if it's a single or multiple target paths
        if isinstance(symlink_data_path, str):
            # Check if target path exists
            if not self.storage_interface.exists(symlink_data_path):
                raise FileNotFoundError(f"{symlink_data_path} does not exist.")

            self.storage_interface.symlink(data_path, symlink_data_path)

        elif isinstance(symlink_data_path, list):
            for item in symlink_data_path:
                # Check if target paths exists
                if not os.path.exists(item):
                    raise FileNotFoundError(f"{item} does not exist.")

                self.storage_interface.symlink(data_path, item)
        else:
            raise ValueError("symlink_data_path must be either a string or a list of strings")

    def deliver_to_targets(self, data_path: str, symlink_data_basepath: str, core_name_options: list, symlink_host_base_path: str = None):
        """
        Recursively collects subdirectories from `data_path`, collects info based on the path structure,
        and creates symlinks to `symlink_data_basepath`.

        Args:
            data_path (str): The base input directory containing the data to be symlinked.
            symlink_data_basepath (str): The base target directory where symlinks will be created.

        Returns:
            None

        Raises:
        FileNotFoundError: If `data_path` or any required target directories do not exist.
        """
        # check if data_path exists
        if not self.storage_interface.exists(data_path):
            raise FileNotFoundError(f"{data_path} does not exist.")

        # collect all sub dirs
        source_paths_list = []
        for root, dirs, files in self.storage_interface.walk(data_path):  # pylint: disable=unused-variable
            if not dirs:
                source_paths_list.append(root)

        # remove duplicates
        source_paths_list = list(set(source_paths_list))

        user_path_not_exist = []
        for path in source_paths_list:
            # split paths
            relative_path = os.path.relpath(path, data_path)
            split_path = relative_path.split(os.sep)
            if len(split_path) >= 5:
                split_path = split_path[:5]
                group, user, asf, project_id, run_id = split_path  # pylint: disable=unused-variable
                info_dict = {"group": group, "user": user, "project_id": project_id, "run_id": run_id}
                # create source path up to the final run_id dir
                source_path_to_runid = os.path.join(
                    data_path, info_dict["group"], info_dict["user"], "genomics-stp", info_dict["project_id"], info_dict["run_id"]
                )

                # create project folders in target path
                permissions_path = os.path.join(symlink_data_basepath, info_dict["group"])
                if self.storage_interface.exists(permissions_path):
                    found_core_name = None
                    for core_dir in core_name_options:
                        project_path = os.path.join(permissions_path, info_dict["user"], core_dir, info_dict["project_id"])
                        if self.storage_interface.exists(project_path):
                            found_core_name = core_dir
                            break
                    if found_core_name is None:
                        found_core_name = "genomics-stp"
                        project_path = os.path.join(permissions_path, info_dict["user"], found_core_name, info_dict["project_id"])
                        self.storage_interface.make_dirs(project_path)

                    # Override symlink path if host provided to deal with symlink paths in containers
                    if symlink_host_base_path is not None:
                        source_path_to_runid = os.path.join(
                            symlink_host_base_path,
                            info_dict["run_id"],
                            "results",
                            "grouped",
                            info_dict["group"],
                            info_dict["user"],
                            "genomics-stp",
                            info_dict["project_id"],
                            info_dict["run_id"],
                        )

                    # symlink data to target path
                    log.info(f"Symlinking {source_path_to_runid} to {project_path}")
                    self.symlink_to_target(source_path_to_runid, project_path)
                else:
                    user_path_not_exist.append(permissions_path)
        if len(user_path_not_exist) > 0:
            log.warning(f"{user_path_not_exist} does not exist.")
            raise FileNotFoundError(f"{user_path_not_exist} does not exist.")
        return True

    def scan_delivery_state(self, source_dir: str, target_dir: str, core_dirname_list: list) -> dict:
        """
        Scans the given source directory for completed pipeline runs and checks
        if corresponding symlinks exist in the target directory. Returns a dictionary
        of runs that are ready to be delivered but do not yet have symlinks in the
        target directory.

        Args:
            source_dir (str): The path to the directory containing pipeline run folders.
            target_dir (str): The path to the directory where the symlinks should be checked.

        Returns:
            dict: A dictionary where the keys are the `run_id` of deliverable runs and
            the values are dictionaries containing the source directory of the completed
            run and the target directory where the symlink should be created.

        Raises:
            FileNotFoundError: If `source_dir` or `target_dir` does not exist.

        Notes:
            - The function expects each pipeline run folder to be structured such that
            the relevant symlinks in the target directory would correspond to a relative
            path derived from the pipeline run folder structure.
            - Only directories that represent completed pipeline runs, as determined by
            `self.check_pipeline_run_complete`, will be considered for potential delivery.
        """
        # check if source_dir exists
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"{source_dir} does not exist.")

        # check if target_dir exists
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"{target_dir} does not exist.")

        # collect run directories and filter for completed runs
        complete_pipeline_runs = []
        abs_source_path = os.path.abspath(source_dir)
        for entry in os.listdir(abs_source_path):
            full_path = os.path.join(abs_source_path, entry)
            if os.path.isdir(full_path):
                if self.check_pipeline_run_complete(full_path):
                    log.debug(f"Found completed run: {entry}")
                    complete_pipeline_runs.append(full_path)
        complete_pipeline_runs.sort()

        # scan target directory for symlinked folders in the grouped directory
        deliverable_runs = {}
        for complete_run in complete_pipeline_runs:
            for root, dirs, files in os.walk(complete_run):  # pylint: disable=unused-variable
                relative_path = os.path.relpath(root, complete_run)
                split_path = relative_path.split(os.sep)

                # Find the group, user, project_id, run_id
                if len(split_path) == 7:
                    split_path = split_path[2:]
                    group, user, genomics_stp, project_id, run_id = split_path  # pylint: disable=unused-variable

                    # build target path
                    target_path = os.path.join(target_dir, *split_path)

                    # Check if the target path exists as a symlink
                    if not os.path.islink(target_path):
                        for core_name in core_dirname_list:
                            genomics_stp = core_name
                            target_path = os.path.join(target_dir, group, user, genomics_stp, project_id, run_id)
                            if os.path.islink(target_path):
                                break
                        if not os.path.islink(target_path):
                            deliverable_runs[split_path[-1]] = {
                                "source": complete_run,
                                "target": target_dir,
                                "group": group,
                                "user": user,
                                "project_id": project_id,
                            }
                        else:
                            log.debug(f"Symlink already exists for {relative_path}")

        return deliverable_runs

    def scan_run_state(
        self,
        raw_dir: str,
        run_dir: str,
        target_dir: str,
        core_dirname_list: list,
        mode: DataTypeMode,
        slurm_user: str = None,
        job_name_suffix: str = None,
        slurm_file: str = None,
    ) -> dict:
        """
        Scans and returns the current state of sequencing and pipeline runs.

        This method checks the specified directories for sequencing and pipeline runs,
        determines their current status, and identifies runs that are ready for delivery.
        The SLURM job status is checked using an optional job name suffix.

        Args:
            raw_dir (str): Directory containing raw sequencing data.
            run_dir (str): Directory containing pipeline run data.
            target_dir (str): Directory where delivery-ready data is stored.
            mode (DataTypeMode): Sequencing mode, either DataTypeMode.ONT or DataTypeMode.ILLUMINA.
            slurm_user (str): Username for checking SLURM job status.
            job_name_suffix (Optional[str]): Optional suffix to append to job names when checking SLURM status.

        Returns:
            dict: A dictionary with run identifiers as keys and their statuses as values.

        Raises:
            FileNotFoundError: If any of the specified directories do not exist.
        """
        # check if source_dir exists
        if not os.path.exists(raw_dir):
            raise FileNotFoundError(f"{raw_dir} does not exist.")

        # check if run_dir exists
        if not os.path.exists(run_dir):
            raise FileNotFoundError(f"{run_dir} does not exist.")

        # check if target_dir exists
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"{target_dir} does not exist.")

        # process raw directories
        run_info = {}
        abs_raw_path = os.path.abspath(raw_dir)
        for entry in os.listdir(abs_raw_path):
            if entry.startswith("."):
                continue
            full_path = os.path.join(abs_raw_path, entry)
            if os.path.isdir(full_path):
                status = "sequencing_in_progress"
                # Check mode and set the appropriate check function
                if mode == DataTypeMode.ONT:
                    check_function = self.check_ont_sequencing_run_complete(full_path)
                elif mode == DataTypeMode.ILLUMINA:
                    check_function = self.check_illumina_sequencing_run_complete(full_path)
                else:
                    raise ValueError(f"Invalid mode: {mode}. Choose a valid DataTypeMode.")

                if check_function:
                    status = "sequencing_complete"
                run_info[entry] = {"status": status}
        run_info = dict(sorted(run_info.items()))

        # process run directories
        abs_run_path = os.path.abspath(run_dir)
        for entry in os.listdir(abs_run_path):
            full_path = os.path.join(abs_run_path, entry)
            if os.path.isdir(full_path):
                status = "pipeline_pending"
                if self.check_pipeline_run_complete(full_path):
                    status = "pipeline_complete"
                else:
                    # check slurm status
                    job_name = entry
                    if job_name_suffix is not None:
                        job_name = job_name_suffix + entry
                    slurm_status = get_job_status(job_name, slurm_user, slurm_file)
                    if slurm_status == "running":
                        status = "pipeline_running"
                    elif slurm_status == "queued":
                        status = "pipeline_queued"
                    else:
                        status = "pipeline_pending"
                run_info[entry]["status"] = status

        # scan for delivery state
        deliverable_runs = self.scan_delivery_state(run_dir, target_dir, core_dirname_list)

        # Scan for delivery state
        for run_id, info in run_info.items():
            if info["status"] == "pipeline_complete":
                if run_id in deliverable_runs:
                    run_info[run_id]["status"] = "ready_to_deliver"
                else:
                    run_info[run_id]["status"] = "delivered"

        # Remove delivered items
        run_info = {run_id: info for run_id, info in run_info.items() if info["status"] != "delivered"}

        return run_info

    def get_latest_mod_time_for_directory(self, root_path):
        """
        Recursively determine the latest modification time within a directory, including all its subdirectories and files.

        This method traverses the directory tree starting from the given `root_path` and checks the modification times of
        all files and subdirectories. It returns the most recent modification time found.

        Args:
            root_path (str): The path to the root directory from which to start the search.

        Returns:
            datetime: A timezone-aware `datetime` object representing the latest modification time of any file or directory
                    within the given `root_path`. If the directory is empty, it returns the modification time of the directory itself.
        """
        latest_mod_time = datetime.fromtimestamp(0, tz=timezone.utc)

        # Get the list of all entries in the root_path
        for entry in os.listdir(root_path):
            entry_path = os.path.join(root_path, entry)

            if os.path.isdir(entry_path):
                # Recursively check subdirectories
                mod_time = self.get_latest_mod_time_for_directory(entry_path)
            elif os.path.isfile(entry_path):
                # Get the modification time of the file
                mod_time = datetime.fromtimestamp(os.path.getmtime(entry_path), tz=timezone.utc)
            else:
                continue
            latest_mod_time = max(latest_mod_time, mod_time)

        # Get the root folder's last modification time
        dir_mod_time = datetime.fromtimestamp(os.path.getmtime(root_path), tz=timezone.utc)
        latest_mod_time = max(latest_mod_time, dir_mod_time)

        return latest_mod_time

    def find_stale_directories(self, path: str, months: int) -> dict:
        """
        Identify directories within a specified path that contain files that have not been modified
        in the last `months` and are not already archived.

        This method traverses the directory tree starting from the given `path` and collects directories
        where the most recently modified file within each directory has not been modified for at least
        `months`. It excludes directories that have already been marked as archived.

        Args:
            path (str): The root directory path to start the search from.
            months (int): The number of months to use as the threshold for determining which directories
                        are considered old. Directories where the latest file modification time is
                        older than `months` will be included.

        Returns:
            dict: A dictionary where each key is the name of a directory that meets the criteria
                (containing files older than `months` and not already archived). The value is a
                dictionary containing:
                    - "path": The full path to the directory.
                    - "days_since_modified": The number of days since the latest file in the directory was last modified.
                    - "last_modified": A string representing the latest modification time of any file in the directory
                    in the format "Month Day, Year, HH:MM:SS UTC".

        Notes:
            - The threshold for old directories is calculated based on an average month length
            of 30.44 days.
            - The method assumes that if any file within a directory is older than the specified threshold,
            the entire directory is considered for archiving.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} does not exist.")

        # Get the current time and calculate the threshold time for archival
        current_time = datetime.now(timezone.utc)
        threshold_time = current_time - timedelta(days=months * 30.44)
        current_time = current_time.replace(tzinfo=timezone.utc)
        threshold_time = threshold_time.replace(tzinfo=timezone.utc)

        # Walk through the directory tree and extract paths older than the threshold, which haven't already been archived
        stale_folders = {}
        for root, dirs, _ in os.walk(path):
            if root == path:
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)

                    # Check all files in the directory
                    latest_mod_time = self.get_latest_mod_time_for_directory(dir_path)

                    if latest_mod_time < threshold_time:
                        formatted_mtime = latest_mod_time.strftime("%B %d, %Y, %H:%M:%S UTC")
                        formatted_machinetime = (
                            latest_mod_time.strftime("%Y-%m-%d %H:%M:%S")
                            + latest_mod_time.strftime("%z")[:3]
                            + ":"
                            + latest_mod_time.strftime("%z")[3:]
                        )
                        days_since_modified = (current_time - latest_mod_time).days

                        if not check_file_exist(dir_path, "archive_readme"):
                            stale_folders[dir_name] = {
                                "path": dir_path,
                                "days_since_modified": days_since_modified,
                                "last_modified_h": formatted_mtime,
                                "last_modified_m": formatted_machinetime,
                            }

        return stale_folders

    def clean_pipeline_output(self, path: str, months: int, ont: DataTypeMode = DataTypeMode.GENERAL):
        """
        Clean up directories and specific files in the pipeline based on their age and type.

        This method performs a series of cleanup tasks for directories within the specified `path`:
        1. Detects and handles stale directories that haven't been modified in the last number of `months`.
        2. Deletes the "work" directory within each stale directory.
        3. If the `ont` parameter is specified as "ont" and the directory contains only one sample,
        it deletes the "results/dorado" directory within the stale directory.

        Args:
            path (str): The root directory path to start the search from.
            months (int): The number of months to use as the threshold for identifying stale directories.
            ont (CleanupType, optional): If set to CleanupType.ONT, additional cleanup is performed for directories with only one sample.
        """

        # Detect folders older than N months
        stale_folders = self.find_stale_directories(path, months)

        # For each run folder in dict, detect and delete "work" dir
        for key in stale_folders:  # pylint: disable=C0206
            run_path = stale_folders[key]["path"]
            work_folder = os.path.join(run_path, "work")
            if os.path.exists(work_folder):
                delete_all_items(work_folder, DeleteMode.DIR_TREE)

            # If the run is ONT and only has 1 sample, delete the run_path/results/dorado folder
            if ont == DataTypeMode.ONT:
                dorado_results = os.path.join(run_path, "results", "dorado")
                samplesheet_found = False

                # Find the samplesheet
                for file in os.listdir(run_path):
                    pattern = "samplesheet"
                    if os.path.isfile(os.path.join(run_path, file)) and pattern in file:
                        # Return the full path to the file
                        samplesheet_path = os.path.join(run_path, file)
                        samplesheet_found = True

                        # Remove dorado_results if the run has only 1 sample
                        with open(samplesheet_path, "r", encoding="utf-8") as file:
                            lines = file.readlines()
                            num_samples = len(lines) - 1  # account for the header

                            if num_samples == 1 and os.path.exists(dorado_results):
                                delete_all_items(dorado_results, DeleteMode.FILES_IN_DIR)
                        break
                if not samplesheet_found:
                    raise FileNotFoundError(f"Samplesheet not found in {path}.")
