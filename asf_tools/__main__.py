#!/usr/bin/env python

"""
Main entry point for command line application
"""

import logging
import os
import sys

import questionary
import rich
import rich.console
import rich.logging
import rich.traceback
import rich_click as click
from rich.table import Table
from rich.text import Text

import asf_tools
from asf_tools.io.data_management import DataTypeMode
from asf_tools.io.storage_interface import InterfaceType, StorageInterface


# Set up logging as the root logger
# Submodules should all traverse back to this
log = logging.getLogger()

# Set up nicer formatting of click cli help messages
click.rich_click.MAX_WIDTH = 100
click.rich_click.USE_RICH_MARKUP = True

# Set up rich stderr console
stderr = rich.console.Console(stderr=True)
stdout = rich.console.Console()

# Set up the rich traceback
rich.traceback.install(console=stderr, width=200, word_wrap=True, extra_lines=1)


def run_asf_tools():
    """
    Print programme header and then use to click for the command line interface.
    """

    # Print header (ANSI Shadow)
    stderr.print("\n\n", highlight=False)
    stderr.print("███████████████████████████████████████████████████████████████████████████████", highlight=False)
    stderr.print("[white]░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░[white]", highlight=False)
    stderr.print("[white]░░░░░█████╗░███████╗███████╗░░░░████████╗░██████╗░░██████╗░██╗░░░░░███████╗░░░░[white]", highlight=False)
    stderr.print("[white]░░░░██╔══██╗██╔════╝██╔════╝░░░░╚══██╔══╝██╔═══██╗██╔═══██╗██║░░░░░██╔════╝░░░░[white]", highlight=False)
    stderr.print("[white]░░░░███████║███████╗█████╗░░░░░░░░░██║░░░██║░░░██║██║░░░██║██║░░░░░███████╗░░░░[white]", highlight=False)
    stderr.print("[white]░░░░██╔══██║╚════██║██╔══╝░░░░░░░░░██║░░░██║░░░██║██║░░░██║██║░░░░░╚════██║░░░░[white]", highlight=False)
    stderr.print("[white]░░░░██║░░██║███████║██║░░░░░░░░░░░░██║░░░╚██████╔╝╚██████╔╝███████╗███████║░░░░[white]", highlight=False)
    stderr.print("[white]░░░░╚═╝░░╚═╝╚══════╝╚═╝░░░░░░░░░░░░╚═╝░░░░╚═════╝░░╚═════╝ ╚══════╝╚══════╝░░░░[white]", highlight=False)
    stderr.print("[white]░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░[white]", highlight=False)
    stderr.print("███████████████████████████████████████████████████████████████████████████████", highlight=False)
    stderr.print("\n", highlight=False)
    stderr.print("[grey25]Program:  asf-tools", highlight=False)
    stderr.print(f"[grey25]Version:  {asf_tools.__version__}", highlight=False)
    stderr.print("[grey25]Author:   Chris Cheshire, Areda Elezi", highlight=False)
    stderr.print("[grey25]Homepage: [link=https://github.com/FrancisCrickInstitute/asf-tools]https://github.com/FrancisCrickInstitute/asf-tools[/]", highlight=False)  # pylint: disable=C0301
    stderr.print("\n", highlight=False)
    stderr.print("███████████████████████████████████████████████████████████████████████████████", highlight=False)
    stderr.print("\n\n", highlight=False)

    # Launch the click cli
    asf_tools_cli()  # pylint: disable=E1120


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(asf_tools.__version__)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Print verbose output to the console.",
)
@click.option("--hide-progress", is_flag=True, default=False, help="Don't show progress bars.")
@click.option("-l", "--log-file", help="Save a verbose log to a file.", metavar="<filename>")
@click.pass_context
def asf_tools_cli(ctx, verbose, hide_progress, log_file):
    """
    asf-tools provides a set of helper tools for technicians in the asf as well as providing
    command line tooling for automation scripts
    """
    # Set the base logger to output DEBUG
    log.setLevel(logging.DEBUG)

    # Set up logs to the console
    log.addHandler(
        rich.logging.RichHandler(
            level=logging.DEBUG if verbose else logging.INFO,
            console=rich.console.Console(stderr=True),
            show_time=False,
            show_path=verbose,  # True if verbose, false otherwise
            markup=True,
        )
    )

    # don't show rich debug logging in verbose mode
    rich_logger = logging.getLogger("rich")
    rich_logger.setLevel(logging.INFO)

    # Set up logs to a file if we asked for one
    if log_file:
        log_fh = logging.FileHandler(log_file, encoding="utf-8")
        log_fh.setLevel(logging.DEBUG)
        log_fh.setFormatter(logging.Formatter("[%(asctime)s] %(name)-20s [%(levelname)-7s]  %(message)s"))
        log.addHandler(log_fh)

    ctx.obj = {
        "verbose": verbose,
        "hide_progress": hide_progress or verbose,  # Always hide progress bar with verbose logging
    }


# asf-tools pipeline subcommands
@asf_tools_cli.group()
@click.pass_context
def pipeline(ctx):
    """
    Commands to manage Pipeline execution
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)


# asf-tools ont gen-demux-run
@pipeline.command("gen-demux-run")
@click.pass_context
@click.option(
    "-s",
    "--source_dir",
    type=click.Path(exists=True),
    required=True,
    help=r"Source directory to look for runs",
)
@click.option(
    "-t",
    "--target_dir",
    type=click.Path(exists=True),
    required=True,
    help=r"Target directory to write runs",
)
@click.option(
    "-m",
    "--mode",
    type=click.Choice([c.value for c in DataTypeMode]),
    required=True,
    help=r"Mode options ONT, Illumina or General",
)
@click.option(
    "-p",
    "--pipeline_dir",
    required=True,
    help=r"Pipeline code directory",
)
@click.option(
    "-n",
    "--nextflow_cache",
    required=True,
    help=r"Nextflow cache directory",
)
@click.option(
    "-w",
    "--nextflow_work",
    required=True,
    help=r"Nextflow work directory",
)
@click.option(
    "-c",
    "--container_cache",
    required=True,
    help=r"Nextflow singularity cache directory",
)
@click.option(
    "-r",
    "--runs_dir",
    required=True,
    help=r"Host path for runs folder",
)
@click.option(
    "--use_api",
    is_flag=True,
    default=False,
    help="Use the Clarity API to generate the samplesheet",
)
@click.option(
    "--contains",
    default=None,
    help="Search for run folders containing this string",
)
@click.option(
    "--samplesheet_only",
    is_flag=True,
    default=False,
    help="Update samplesheets only for all runs in target folder. Contains will still restrict this list.",
)
@click.option(
    "--nextflow_version",
    default=None,
    help="Set the version of Nextflow to use in the sbatch header",
)
def gen_demux_run(ctx,  # pylint: disable=W0613 disable=too-many-positional-arguments
                      source_dir,
                      target_dir,
                      mode,
                      pipeline_dir,
                      nextflow_cache,
                      nextflow_work,
                      container_cache,
                      runs_dir,
                      use_api,
                      contains,
                      samplesheet_only,
                      nextflow_version):
    """
    Create run directory for the ONT demux pipeline
    """
    # from nf_core.modules import ModuleInstall
    from asf_tools.api.clarity.clarity_helper_lims import ClarityHelperLims  # pylint: disable=C0415
    from asf_tools.io.data_management import DataManagement  # pylint: disable=C0415
    from asf_tools.nextflow.gen_demux_run import run_cli  # pylint: disable=C0415

    try:
        api = ClarityHelperLims()
        storage_interface = StorageInterface(InterfaceType.LOCAL)
        data_management = DataManagement(storage_interface)
        exit_status = run_cli(
            api,
            storage_interface,
            data_management,
            DataTypeMode(mode),
            source_dir,
            target_dir,
            contains,
            samplesheet_only,
            use_api,
            nextflow_version,
            nextflow_cache,
            nextflow_work,
            container_cache,
            pipeline_dir,
            runs_dir,
        )

        if not exit_status:
            sys.exit(1)
    except (UserWarning, LookupError) as e:
        log.error(e)
        sys.exit(1)

# asf-tools ont deliver-to-targets
@pipeline.command("deliver-to-targets")
@click.pass_context
@click.option(
    "-s",
    "--source_dir",
    type=click.Path(exists=True),
    required=True,
    help="Source directory. For non-interactive mode, this is the run directory of the demux pipeline; \
        for interactive mode, this is the source directory containing all the runs.",
)
@click.option(
    "-t",
    "--target_dir",
    type=click.Path(exists=True),
    required=True,
    help="Target directory",
)
@click.option(
    "-d",
    "--host_delivery_folder",
    type=click.Path(exists=False),
    required=False,
    help="Use when running inside a container to ensure sylinks are created in the correct location",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    default=False,
    help="Run in interactive mode",
)
def deliver_to_targets(
    ctx,  # pylint: disable=W0613
    source_dir,
    target_dir,
    host_delivery_folder,
    interactive,):
    """
    Symlinks demux outputs to the user directory
    """  # pylint: disable=too-many-positional-arguments
    from asf_tools.io.data_management import DataManagement  # pylint: disable=C0415

    dm = DataManagement(StorageInterface(InterfaceType.LOCAL))
    if interactive is False:
        # Take the source / target literally and deliver
        dm.deliver_to_targets(
            source_dir,
            target_dir,
            ["asf", "genomics-stp"],
            host_delivery_folder
        )
    else:
        # Interactivly scan for delivery targets
        scan_result = dm.scan_delivery_state(
            source_dir,
            target_dir,
            ["asf", "genomics-stp"],
        )

        # If no runs are found, exit
        if not scan_result:
            log.info("No deliverable runs found.")
            return

        # Display table of scan results
        table = Table(title="Deliverable Runs", show_header=True, header_style="bold magenta")
        table.add_column("Run ID", style="bold")
        table.add_column("Group")
        table.add_column("User")
        table.add_column("Project Id")
        for run_id, data in scan_result.items():
            table.add_row(run_id, data["group"], data["user"], data["project_id"])
        stdout.print(table)

        # User choice run ids
        results = questionary.checkbox(
            'Select Run Ids to deliver',
            choices=scan_result.keys()).ask()

        # Confirm selected runs
        if results:
            stdout.print("\n")
            table = Table(title="Selected Runs", show_header=True, header_style="bold magenta")
            table.add_column("Run ID", style="bold")
            for result in results:
                table.add_row(result)
            stdout.print(table)
            confirmation = questionary.confirm("Are you sure you want to deliver the selected runs?").ask()

            # Deliver the selected runs
            if confirmation:
                for result in results:
                    log.info(f"Delivering {result}")
                    dm.deliver_to_targets(
                        os.path.join(source_dir, result, "results", "grouped"),
                        target_dir,
                        ["asf", "genomics-stp"],
                        host_delivery_folder
                    )

# asf-tools ont scan-run-state
@pipeline.command("scan-run-state")
@click.pass_context
@click.option(
    "--raw_dir",
    type=click.Path(exists=True),
    required=True,
    help="ONT sequencing directory",
)
@click.option(
    "--run_dir",
    type=click.Path(exists=True),
    required=True,
    help="ONT pipeline directory",
)
@click.option(
    "--target_dir",
    type=click.Path(exists=True),
    required=True,
    help="Target data delivery directory",
)
@click.option(
    "--mode",
    type=click.Choice([c.value for c in DataTypeMode]),
    required=True,
    help="Mode options, ONT or Illumina",
)
@click.option(
    "--slurm_user",
    required=False,
    help="Slurm user to check job status",
)
@click.option(
    "--job_prefix",
    required=False,
    help="Slurm job name prefix",
)
@click.option(
    "--slurm_file",
    required=False,
    help="Slurm job output file",
)
def scan_run_state(  # pylint: disable=too-many-positional-arguments
    ctx,  # pylint: disable=W0613
    raw_dir,
    run_dir,
    target_dir,
    mode,
    slurm_user,
    job_prefix,
    slurm_file):
    """
    Scans the state ONT sequencing runs
    """
    from asf_tools.io.data_management import DataManagement  # pylint: disable=C0415

    # Scan for run id states
    dm = DataManagement(StorageInterface(InterfaceType.LOCAL))
    scan_result = dm.scan_run_state(
        raw_dir,
        run_dir,
        target_dir,
        ["asf", "genomics-stp"],
        DataTypeMode(mode),
        slurm_user,
        job_prefix,
        slurm_file,
    )

    def get_state_color(status):
        if status == "sequencing_in_progress":
            return "red"
        if status == "sequencing_complete":
            return "rgb(255,165,0)"
        if status == "pipeline_pending":
            return "yellow"
        if status == "pipeline_queued":
            return "yellow"
        if status == "pipeline_running":
            return "rgb(173,216,230)"
        return "green"

    # Display table of scan results
    table = Table(title="Run state", show_header=True, header_style="bold magenta")
    table.add_column("Run ID", style="bold")
    table.add_column("State")
    for run_id, data in scan_result.items():
        state_text = Text(data["status"], style=get_state_color(data["status"]))
        table.add_row(run_id, state_text)
    stdout.print(table)

# asf-tools ont upload-report
@pipeline.command("upload-report")
@click.pass_context
@click.option(
    "--data-file",
    type=click.Path(exists=True),
    required=True,
    help="Pickle data file to upload",
)
@click.option(
    "--run-id",
    required=True,
    help="Run id of the data file",
)
@click.option(
    "--report-type",
    required=True,
    help="The report type",
)
@click.option(
    "--upload-table",
    required=True,
    help="Target data delivery directory",
)
@click.option(
    "--table_overide",
    required=False,
    help="Override the table suffix",
)

def upload_report(  # pylint: disable=too-many-positional-arguments
    ctx,  # pylint: disable=W0613
    data_file,
    run_id,
    report_type,
    upload_table,
    table_overide):
    """
    Scans the state ONT sequencing runs
    """
    from asf_tools.config.toml_loader import load_toml_file  # pylint: disable=C0415
    from asf_tools.database.crud import DatabaseCrud  # pylint: disable=C0415
    from asf_tools.database.db import Database, construct_postgres_url  # pylint: disable=C0415

    log.info(f"Uploading report for {run_id} to {upload_table}")

    # Load config
    config = load_toml_file()
    db_host = config["database"]["automation_prod"]["host"]
    db_port = config["database"]["automation_prod"]["port"]
    db_name = config["database"]["automation_prod"]["database"]
    db_user = config["database"]["automation_prod"]["username"]
    db_pass = config["database"]["automation_prod"]["password"]
    db_suffix = config["database"]["automation_prod"]["table_suffix"]

    if table_overide:
        db_suffix = table_overide
    log.info(f"Using table suffix {db_suffix}")

    # Init DB
    db = Database(construct_postgres_url(db_user, db_pass, db_host, db_port, db_name))
    crud = DatabaseCrud(table_name=f"{upload_table}_{db_suffix}")

    # Load data
    with open(data_file, "rb") as f:
        binary_data = f.read()

    # Check if the run exists and upload
    with db.db_session() as db:
        run = crud.get_simple(db, "id", run_id, as_dict=True)

        if len(run) == 0:
            crud.create(db, {"id": run_id, "type": report_type, "data": binary_data})
            log.info(f"Run {run_id} not found in {upload_table}, creating new entry")
        else:
            crud.update(db, run_id, {"id": run_id, "type": report_type, "data": binary_data})
            log.info(f"Run {run_id} found in {upload_table}, updating entry")

    log.info("Upload complete")

# Main script is being run - launch the CLI
if __name__ == "__main__":
    run_asf_tools()
