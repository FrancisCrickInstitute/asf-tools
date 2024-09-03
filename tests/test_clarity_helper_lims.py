"""
Clarity helper API Tests
"""

import os
import unittest

import pytest
from requests.exceptions import ConnectionError, HTTPError  # pylint: disable=redefined-builtin

from asf_tools.api.clarity.models import Stub

from .mocks.clarity_helper_lims_mock import ClarityHelperLimsMock


API_TEST_DATA = "tests/data/api/clarity"


class TestClarityHelperLims(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    @classmethod
    def setUpClass(cls):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
        cls.api = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
        cls.api.load_tracked_requests(data_file_path)
        cls.data_file_path = data_file_path

    @classmethod
    def tearDownClass(cls):
        """Teardown API connection"""
        cls.api.save_tracked_requests(cls.data_file_path)

    def test_clarity_helper_get_artifacts_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_artifacts_from_runid(None)

    def test_clarity_helper_get_artifacts_from_runid_isinvalid(self):
        """
        Pass runid that does not exist
        """

        # Setup
        runid = "fake_runid"

        # Test and Assert
        with self.assertRaises(KeyError):
            self.api.get_artifacts_from_runid(runid)

    def test_clarity_helper_get_samples_from_artifacts_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_samples_from_artifacts(None)

    def test_clarity_helper_get_samples_from_artifacts_isinvalid(self):
        """
        Pass an artifact that does not exist
        """

        # Setup
        artifacts_list = [Stub(id="TestID", uri="https://asf-claritylims.thecrick.org/api/v2/artifacts/TEST", name=None, limsid="TestID")]

        # Test and Assert
        with self.assertRaises((HTTPError, ConnectionError)):
            self.api.get_samples_from_artifacts(artifacts_list)

    def test_clarity_helper_get_sample_info_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_info(None)

    def test_clarity_helper_get_sample_barcode_from_runid_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.get_sample_barcode_from_runid(None)

    def test_clarity_helper_collect_samplesheet_info_isnone(self):
        """
        Pass None to method
        """

        # Test and Assert
        with self.assertRaises(ValueError):
            self.api.collect_samplesheet_info(None)

    def test_alternative_barcode(self):

        barcode = self.api.alternative_barcode("22G2JFLT4")
        print(barcode)

        raise ValueError


class TestClarityHelperLimsyWithFixtures:
    """Class for clarity tests with fixtures"""

    @pytest.fixture(scope="class")
    def api(self, request):
        """Setup API connection"""
        data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
        lims = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
        lims.load_tracked_requests(data_file_path)
        request.addfinalizer(lambda: lims.save_tracked_requests(data_file_path))
        yield lims

    @pytest.mark.parametrize("runid,expected", [("20240417_1729_1C_PAW45723_05bb74c5", 1), ("20240625_1734_2F_PAW20497_d0c3cbb5", 1)])
    def test_clarity_helper_get_artifacts_from_runid_valid(self, api, runid, expected):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Test
        artifacts = api.get_artifacts_from_runid(runid)

        # Assert
        assert len(artifacts) == expected

    @pytest.mark.parametrize("run_id,expected_sample_quantity", [("B_04-0004-S6_DT", 1), ("462-24_MPX-seq", 4)])  # Illumina  # ONT
    def test_clarity_helper_get_samples_from_artifacts_isvalid(self, api, run_id, expected_sample_quantity):
        """
        Pass real artifact IDs and test expected number of samples back
        """

        # Set up
        artifact = api.get_artifacts(name=run_id)

        # Test
        get_samples = api.get_samples_from_artifacts(artifact)

        # Assert
        assert len(get_samples) == expected_sample_quantity

    @pytest.mark.parametrize(
        "sample_id,expected_dict",
        [
            (
                "KAN6921A20",
                {
                    "KAN6921A20": {
                        "sample_name": "99-005-0496_98-290_bp",
                        "group": "swantonc",
                        "user": "nnennaya.kanu",
                        "project_id": "DN24086",
                        "project_limsid": "KAN6921",
                        "project_type": "WGS",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "None",
                    }
                },
            ),  # ONT
            (
                "ALV729A45",
                {
                    "ALV729A45": {
                        "sample_name": "MAM040P_5",
                        "group": "ogarraa",
                        "user": "marisol.alvarez-martinez",
                        "project_id": "RN20066",
                        "project_limsid": "ALV729",
                        "project_type": "mRNA-Seq from RNA",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "RNA-Seq",
                    }
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_info_isvalid(self, api, sample_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """

        # Set up
        sample = api.get_samples(search_id=sample_id)

        # Test
        get_info = api.get_sample_info(sample.id)

        # Assert
        assert get_info == expected_dict

    @pytest.mark.parametrize(
        "runid,expected_sample_quantity",
        [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4),
            ("HWNT7BBXY", 9),
            ("20240625_1734_2F_PAW20497_d0c3cbb5", 1),
            ("PAW45729_20240715_1306_20108e83", 48),
        ],
    )
    def test_clarity_helper_collect_sample_info_from_runid(self, api, runid, expected_sample_quantity):
        """
        Pass real run IDs and test expected number of samples stored in the dictionary output
        """

        # Test
        sample_dict = api.collect_sample_info_from_runid(runid)

        # Assert
        assert len(sample_dict) == expected_sample_quantity

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {"barcode": "BC01 (AAGAAAGTTGTCGGTGTCTTTGTG)"},
                    "VIV6902A2": {"barcode": "BC02 (TCGATTCCGTTTGTAGTCGTCTGT)"},
                    "VIV6902A3": {"barcode": "BC03 (GAGTCTTGTGTCCCAGTTACCAGG)"},
                    "VIV6902A4": {"barcode": "BC04 (TTCGGATTCTATCGTGTTTCCCTA)"},
                },
            ),  # ONT
            ("20240625_1734_2F_PAW20497_d0c3cbb5", {}),
            (
                "20240807_1248_P2S-02348-A_PAW31464_90cccf6c",
                {
                    "SWA6667A7": {"barcode": "BC01 (AAGAAAGTTGTCGGTGTCTTTGTG)"},
                    "SWA6667A8": {"barcode": "BC02 (TCGATTCCGTTTGTAGTCGTCTGT)"},
                    "SWA6667A37": {"barcode": "BC03 (GAGTCTTGTGTCCCAGTTACCAGG)"},
                    "SWA6667A38": {"barcode": "BC04 (TTCGGATTCTATCGTGTTTCCCTA)"},
                    "SWA6667A39": {"barcode": "BC05 (CTTGTCCAGGGTTTGTGTAACCTT)"},
                    "SWA6667A41": {"barcode": "BC06 (TTCTCGCAAAGGCAGAAAGTAGTC)"},
                    "201C-2072202": {"barcode": "BC07 (GTGTTACCGTGGGAATGAATCCTT)"},
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_barcode_from_runid_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        barcode_dict = api.get_sample_barcode_from_runid(run_id)

        # Assert
        assert barcode_dict == expected_dict

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {
                        "barcode": "BC01 (AAGAAAGTTGTCGGTGTCTTTGTG)",
                        "sample_name": "BR1_D0",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                    },
                    "VIV6902A2": {
                        "barcode": "BC02 (TCGATTCCGTTTGTAGTCGTCTGT)",
                        "sample_name": "BR1_D7",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                    },
                    "VIV6902A3": {
                        "barcode": "BC03 (GAGTCTTGTGTCCCAGTTACCAGG)",
                        "sample_name": "BR2_D0",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                    },
                    "VIV6902A4": {
                        "barcode": "BC04 (TTCGGATTCTATCGTGTTTCCCTA)",
                        "sample_name": "BR2_D7",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                    },
                },
            ),  # ONT
            (
                "HWNT7BBXY",
                {
                    "TLG66A2839": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "A_LTX265_NP_T1_FR1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 40 H05 (CTGAGCCA)",
                    },
                    "TLG66A2840": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "L_LTX877_MR_T1_FR4",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 41 A06 (AGCCATGC)",
                    },
                    "TLG66A2841": {
                        "sample_name": "L_LTX877_MR_T1_FR5",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "project_type": "WES",
                        "barcode": "SXT 42 B06 (GTACGCAA)",
                    },
                    "TLG66A2842": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "A_LTX1310_MR_T1_FR3",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 43 C06 (AGTACAAG)",
                    },
                    "TLG66A2843": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "A_LTX1331_BR_T1_FR1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 44 D06 (ACATTGGC)",
                    },
                    "TLG66A2844": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1350_BR_T1_FR3",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 45 E06 (ATTGAGGA)",
                    },
                    "TLG66A2845": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1335_SU_FLN1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 46 F06 (GTCGTAGA)",
                    },
                    "TLG66A2848": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1335_BS_GL",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 03 C01 (AACGTGAT)",
                    },
                    "TLG66A2849": {
                        "project_limsid": "TLG66",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "Whole Exome",
                        "sample_name": "U_LTX1335_BP_LN1",
                        "group": "swantonc",
                        "user": "tracerx.tlg",
                        "project_id": "TRACERx_Lung",
                        "project_type": "WES",
                        "barcode": "SXT 04 D01 (CACTTCGA)",
                    },
                },
            ),  # Illumina
            (
                "20240625_1734_2F_PAW20497_d0c3cbb5",
                {
                    "KAN6921A20": {
                        "sample_name": "99-005-0496_98-290_bp",
                        "group": "swantonc",
                        "user": "nnennaya.kanu",
                        "project_id": "DN24086",
                        "project_limsid": "KAN6921",
                        "project_type": "WGS",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "None",
                    }
                },
            ),  # ONT, no barcode info
        ],
    )
    def test_clarity_helper_collect_samplesheet_info_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        merged_dict = api.collect_samplesheet_info(run_id)

        # Assert
        assert merged_dict == expected_dict


