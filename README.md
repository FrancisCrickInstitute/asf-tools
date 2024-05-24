# asf-tools

ASF Tools command line tool-kit for ASF operations.

## Description

- **Author**: Chris Cheshire
- **Date**: May 2024


ASF Tools is a command line application that performs repetitive functions useful to internal ASF operations that can be run by a user or via automation. It also acts as a toolkit kit to interact with services such as the LIMS

## Getting Started

ASF tools exists as a containerised application on nemo. The easiest way to interact with asf tools is to run the script packaged with [asf-automation-scripts](https://github.com/FrancisCrickInstitute/asf-automation-scripts). Running `asf_tools.sh` will spin up the application on nemo and provide a command line interface.

## Usage

### General Syntax

```sh
asf_tools [OPTIONS] COMMAND [ARGS]...
```

### Options

- `-h`, `--help`: Show the help message and exit.
- `-v`, `--verbose`: Print verbose output to the console.
- `--hide-progress`: Don't show progress bars.
- `-l`, `--log-file <filename>`: Save a verbose log to a file.


### Commands

#### ont

Commands to manage ONT data.

##### gen-demux-run

Create run directory for the ONT demux pipeline.

###### Syntax

```sh
asf_tools ont gen-demux-run [OPTIONS]
```

###### Options

- `-s`, `--source_dir PATH`: Source directory to look for runs (required).
- `-t`, `--target_dir PATH`: Target directory to write runs (required).
- `-p`, `--pipeline_dir PATH`: Pipeline code directory (required).
- `-n`, `--nextflow_cache PATH`: Nextflow cache directory (required).
- `-w`, `--nextflow_work PATH`: Nextflow work directory (required).
- `-c`, `--container_cache PATH`: Nextflow singularity cache directory (required).
- `-r`, `--runs_dir PATH`: Host path for runs folder (required).
- `-e`, `--execute`: Trigger pipeline run on cluster.

## Credits, contacts

- Chris Cheshire (Pipelines Technology Core)

Please contact chris.cheshire@crick.ac.uk

## Status

In Development
