"""
Helper functions for data management
"""

import logging
import os
import subprocess

from asf_tools.io.utils import check_file_exist
from asf_tools.slurm.utils import get_job_status


# Set up logging as the root logger
log = logging.getLogger()


class DataManagement:
    """
    Helper functions for data management
    """

    def check_pipeline_run_complete(self, run_dir: str):
        """
        Check if a pipeline run directory is complete by checking for the presence of the `workflow_complete` file.

        Args:
        - run_dir (str): Path to the run directory.

        Returns:
        - bool: True if the run directory is complete, False otherwise.
        """
        completed_file = os.path.join(run_dir, "results", "pipeline_info", "workflow_complete.txt")
        return os.path.exists(completed_file)

    def check_ont_sequencing_run_complete(self, run_dir: str):
        """
        Check if an ONT sequencing run is complete by checking for the presence of the `sequencing_summary`
        file.

        Args:
        - run_dir (str): Path to the run directory.
        """
        return check_file_exist(run_dir, "sequencing_summary*")

    def symlink_to_target(self, data_path: str, symlink_data_path):
        """
        Creates symbolic links for a given data path in one or multiple destination paths.

        Args:
        - data_path (str): Path to the source data to be symlinked.
        - symlink_data_path (Union[str, list]): Single path or list of paths where the symlinks should be created.

        Raises:
        - ValueError: If symlink_data_path is neither a string nor a list.
        - subprocess.CalledProcessError: If the subprocess command fails.

        Example usage:
        transfer_data('/path/to/source', '/path/to/destination')
        transfer_data('/path/to/source', ['/path/to/dest1', '/path/to/dest2'])
        """

        # Check if source paths exists - commented out as I need to be able to symlink to non-existent paths
        # if not os.path.exists(data_path):
        #     raise FileNotFoundError(f"{data_path} does not exist.")

        # Check if it's a single or multiple target paths
        if isinstance(symlink_data_path, str):
            # Check if target path exists
            if not os.path.exists(symlink_data_path):
                raise FileNotFoundError(f"{symlink_data_path} does not exist.")

            cmd = f"ln -sfn {data_path} {symlink_data_path}"
            subprocess.run(cmd, shell=True, check=True)

        elif isinstance(symlink_data_path, list):
            for item in symlink_data_path:
                # Check if target paths exists
                if not os.path.exists(item):
                    raise FileNotFoundError(f"{item} does not exist.")

                cmd = f"ln -sfn {data_path} {item}"
                subprocess.run(cmd, shell=True, check=True)
        else:
            raise ValueError("symlink_data_path must be either a string or a list of strings")

    def deliver_to_targets(self, data_path: str, symlink_data_basepath: str, symlink_host_base_path: str = None):
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
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"{data_path} does not exist.")

        # collect all sub dirs
        source_paths_list = []
        for root, dirs, files in os.walk(data_path):  # pylint: disable=unused-variable
            if not dirs:
                source_paths_list.append(root)

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
                    data_path, info_dict["group"], info_dict["user"], "asf", info_dict["project_id"], info_dict["run_id"]
                )

                # create project folders in target path
                permissions_path = os.path.join(symlink_data_basepath, info_dict["group"])
                if os.path.exists(permissions_path):
                    project_path = os.path.join(permissions_path, info_dict["user"], "asf", info_dict["project_id"])
                    if not os.path.exists(project_path):
                        os.makedirs(project_path, exist_ok=True)

                    # Override symlink path if host provided to deal with symlink paths in containers
                    if symlink_host_base_path is not None:
                        source_path_to_runid = os.path.join(
                            symlink_host_base_path,
                            info_dict["run_id"],
                            "results",
                            "grouped",
                            info_dict["group"],
                            info_dict["user"],
                            "asf",
                            info_dict["project_id"],
                            info_dict["run_id"],
                        )

                    # symlink data to target path
                    self.symlink_to_target(source_path_to_runid, project_path)
                else:
                    user_path_not_exist.append(permissions_path)
        if len(user_path_not_exist) > 0:
            log.warning(f"{user_path_not_exist} does not exist.")
            raise FileNotFoundError(f"{user_path_not_exist} does not exist.")
        return True

    def scan_delivery_state(self, source_dir: str, target_dir: str):
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
                    complete_pipeline_runs.append(os.path.join(abs_source_path, entry))
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
                    group, user, asf, project_id, run_id = split_path  # pylint: disable=unused-variable

                    # build target path
                    target_path = os.path.join(target_dir, *split_path)

                    # Check if the target path exists as a symlink
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

    def scan_run_state(self, raw_dir: str, run_dir: str, target_dir: str, slurm_user: str, job_name_suffix: str = None) -> dict:
        """
        Scans and returns the current state of sequencing and pipeline runs.

        This method checks the specified directories for sequencing and pipeline runs, 
        determines their current status, and identifies runs that are ready for delivery.
        The SLURM job status is checked using an optional job name suffix.

        Args:
            raw_dir (str): Directory containing raw sequencing data.
            run_dir (str): Directory containing pipeline run data.
            target_dir (str): Directory where delivery-ready data is stored.
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
                if self.check_ont_sequencing_run_complete(full_path):
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
                    slurm_status = get_job_status(job_name, slurm_user)
                    if slurm_status == "running":
                        status = "pipeline_running"
                    elif slurm_status == "queued":
                        status = "pipeline_queued"
                    else:
                        status = "pipeline_pending"
                run_info[entry]["status"] = status

        # scan for delivery state
        deliverable_runs = self.scan_delivery_state(run_dir, target_dir)

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
