import pytest

from asf_tools.illumina.illumina_data_wrangling import generate_illumina_demux_samplesheets


def test_generate_illumina_demux_samplesheets():
    file = "./tests/data/illumina/RunInfo.xml"
    results = generate_illumina_demux_samplesheets(file)
    print(results)

    # Assert
    raise ValueError
