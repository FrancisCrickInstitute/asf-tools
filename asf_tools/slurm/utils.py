"""
This module provides utility functions for the SLURM workload manager.
"""

import logging
import subprocess

log = logging.getLogger()


def get_job_status(job_name: str, user_name: str) -> str:
    """
    Retrieve the status of a job from the SLURM job scheduler using the `squeue` command.

    Args:
        job_name (str): The name of the job to check the status of.
        user_name (str): The username of the user who submitted the job.

    Returns:
        str: The status of the job, which can be 'running' if the job is currently running,
             'queued' if the job is pending in the queue, or `None` if the job is not found.

    Raises:
        subprocess.CalledProcessError: If the `squeue` command fails to execute.

    Notes:
        - The function assumes that the `squeue` command is available in the system's PATH.
        - The job status is determined by parsing the output of `squeue`. The job status codes checked are:
          'R' or 'CG' for running/completing jobs, and 'PD' for queued jobs.
        - If the job name is not found in the `squeue` output, the function returns `None`.
    """
    # Run the squeue command and capture the output
    command = f"/usr/bin/squeue -u {user_name} --format=\"%.8i %.7P %.52j %.8u %.2t %.10M %.6D %R\""
    log.debug("Running command: %s", " ".join(command))
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, check=True, shell=True)

    # Split the output into lines
    lines = result.stdout.strip().split("\n")

    # Iterate through lines to find the job
    for line in lines:
        parts = line.split()

        job_nm, job_status = parts[2], parts[4]
        if job_nm == job_name:
            if job_status in ["R", "CG"]:  # Running or Completing
                return "running"
            elif job_status in ["PD"]:  # Pending (queued)
                return "queued"

    # If the job name was not found in the list
    return None
