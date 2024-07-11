#!/usr/bin/env python

"""
Main entry point for command line application
"""

import logging
import sys

import rich
import rich.console
import rich.logging
import rich.traceback
import rich_click as click

import asf_tools


# Set up logging as the root logger
# Submodules should all traverse back to this
log = logging.getLogger()

# Set up nicer formatting of click cli help messages
click.rich_click.MAX_WIDTH = 100
click.rich_click.USE_RICH_MARKUP = True

# Setup command groups
click.rich_click.COMMAND_GROUPS = {
    "asf-tools": [
    ],
    "asf-tools ont": [
        {
            "name": "Manual",
            "commands": [],
        },
        {
            "name": "Automation",
            "commands": ["gen-demux-run"],
        },
    ]
}

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


# asf-tools ont subcommands
@asf_tools_cli.group()
@click.pass_context
def ont(ctx):
    """
    Commands to manage ONT data
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)


# asf-tools ont gen-demux-run
@ont.command("gen-demux-run")
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
def ont_gen_demux_run(ctx,  # pylint: disable=W0613
                      source_dir,
                      target_dir,
                      pipeline_dir,
                      nextflow_cache,
                      nextflow_work,
                      container_cache,
                      runs_dir,
                      use_api,
                      contains,
                      samplesheet_only):
    """
    Create run directory for the ONT demux pipeline
    """
    # from nf_core.modules import ModuleInstall
    from asf_tools.ont.ont_gen_demux_run import OntGenDemuxRun  # pylint: disable=C0415

    try:
        function = OntGenDemuxRun(
            source_dir,
            target_dir,
            pipeline_dir,
            nextflow_cache,
            nextflow_work,
            container_cache,
            runs_dir,
            use_api,
            contains,
            samplesheet_only
        )
        exit_status = function.run()
        if not exit_status:
            sys.exit(1)
    except (UserWarning, LookupError) as e:
        log.error(e)
        sys.exit(1)

# # asf-tools data management subcommands
# @data_tools.command("symlink-folders") #needs a data_tools function written
# @click.pass_context
# @click.option(
#     "-s",
#     "--source_dir",
#     type=click.Path(exists=True),
#     required=True,
#     help=r"Source directory with data",
# )
# @click.option(
#     "-t",
#     "--target_dir",
#     type=click.Path(exists=True),
#     required=True,
#     help=r"Target directory to symlink data to",
# )
# def data_symlink(source_dir, target_dir):
#     from asf_tools.ont.data_cli import DataManagementCli

#     try:
#         DataManagementCli(source_dir, target_dir)
#     except (UserWarning, LookupError) as e:
#         log.error(e)
#         sys.exit(1)

# Main script is being run - launch the CLI
if __name__ == "__main__":
    run_asf_tools()
