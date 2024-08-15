# asf-tools

ASF Tools command line tool-kit for ASF operations.

## Description

- **Author**: Chris Cheshire, Areda Elezi
- **Status**: In Production


ASF Tools is a command-line application designed to streamline and automate repetitive tasks within ASF operations. It provides a suite of utilities for managing data, interacting with internal services such as the LIMS, and supporting automation workflows.

## Getting Started

ASF tools exists as a containerised application on nemo. The easiest way to interact with asf tools is to run the scripts packaged with [asf-automation-scripts](https://github.com/FrancisCrickInstitute/asf-automation-scripts) in the `scripts` folder. A operations must be run from the `scripts` folder where the `config.sh` file is. For example to run asf_tools with your own arguments, run `./asf-automation-scripts/asf_tools.sh ARGS`.

## Usage

### Commands

#### ont

Commands for managing Nanopore (ONT) data.

##### `gen-demux-run`

Creates a run directory for the ONT demux pipeline.

###### Syntax

```sh
asf_tools ont gen-demux-run [OPTIONS]
```

###### Options

- `-s`, `--source_dir <PATH>`: Source directory to look for runs (required).
- `-t`, `--target_dir <PATH>`: Target directory to write runs (required).
- `-p`, `--pipeline_dir <PATH>`: Pipeline code directory (required).
- `-n`, `--nextflow_cache <PATH>`: Nextflow cache directory (required).
- `-w`, `--nextflow_work <PATH>`: Nextflow work directory (required).
- `-c`, `--container_cache <PATH>`: Nextflow Singularity cache directory (required).
- `-r`, `--runs_dir <PATH>`: Host path for the runs folder (required).
- `--use_api`: Utilize the Clarity API to generate the samplesheet.
- `--contains <STRING>`: Filter run folders by a substring.
- `--samplesheet_only`: Update samplesheets only for all runs in the target folder.
- `--nextflow_version <VERSION>`: Specify the Nextflow version to use in the sbatch header.

##### `deliver-to-targets`

Symlinks demux outputs to the user directory.

###### Syntax

```sh
asf_tools ont deliver-to-targets [OPTIONS]
```

###### Options

- `-s`, `--source_dir <PATH>`: Source directory (required).
- `-t`, `--target_dir <PATH>`: Target directory (required).
- `-d`, `--host_delivery_folder <PATH>`: Host delivery folder path.
- `-i`, `--interactive`: Run in interactive mode to select runs manually.

## Contact

Please contact chris.cheshire@crick.ac.uk for any questions.
