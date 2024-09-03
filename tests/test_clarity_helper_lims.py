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
            (
                "SKO6875A940",
                {
                    "SKO6875A940": {
                        "sample_name": "L12120",
                        "group": "skoglundp",
                        "user": "pontus.skoglund",
                        "project_id": "PM24043",
                        "project_limsid": "SKO6875",
                        "project_type": "Other",
                        "reference_genome": "Other",
                        "data_analysis_type": "None",
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
        print(get_info)

        # Assert
        assert get_info == expected_dict

    @pytest.mark.parametrize(
        "runid,expected_sample_quantity",
        [
            ("20240417_1729_1C_PAW45723_05bb74c5", 4),
            ("HWNT7BBXY", 9),
            ("20240625_1734_2F_PAW20497_d0c3cbb5", 1),
            ("PAW45729_20240715_1306_20108e83", 48),
            ("ASF_A05136-P27", 1),
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
                "22G2JFLT4",
                {
                    "SOA6876A276": {"barcode": "32307 AGL IP7_85 and IP5_435 (AGACCAAT-AACTCCGG)"},
                    "SOA6876A277": {"barcode": "28501 AGL IP7_75 and IP5_469 (ACCAAGAT-ATTGGTCT)"},
                    "SOA6876A278": {"barcode": "10824 AGL IP7_29 and IP5_456 (ACTCTTGG-AGCTCCAA)"},
                    "SOA6876A279": {"barcode": "70456 AGL IP7_184 and IP5_568 (CGTTCGCT-AGCGAACG)"},
                    "SOA6876A280": {"barcode": "55832 AGL IP7_146 and IP5_536 (CGTAGATC-CAATTGCA)"},
                    "SOA6876A281": {"barcode": "61953 AGL IP7_162 and IP5_513 (TGGTCCTG-TAACGAAG)"},
                    "SOA6876A282": {"barcode": "48877 AGL IP7_128 and IP5_493 (AGCAAGGC-GCCGTCCG)"},
                    "SOA6876A283": {"barcode": "60014 AGL IP7_157 and IP5_494 (TGGTTGAC-TCTGACTG)"},
                    "SOA6876A284": {"barcode": "20386 AGL IP7_54 and IP5_418 (TGCTCTTC-AGGTCGGA)"},
                    "SOA6876A285": {"barcode": "15828 AGL IP7_42 and IP5_468 (ATAATGGT-AGGTAGTT)"},
                    "SOA6876A286": {"barcode": "24256 AGL IP7_64 and IP5_448 (TCAGTTAA-TTAACTGA)"},
                    "SOA6876A287": {"barcode": "22351 AGL IP7_59 and IP5_463 (CCGGCGAC-TTCTAATG)"},
                    "SOA6876A288": {"barcode": "8463 AGL IP7_23 and IP5_399 (GGCTTGAA-TTGACTAT)"},
                    "SOA6876A289": {"barcode": "3483 AGL IP7_10 and IP5_411 (GGCCTCCT-AATCGCAT)"},
                    "SOA6876A290": {"barcode": "25369 AGL IP7_67 and IP5_409 (CTATTCAT-AAGAGCGC)"},
                    "SOA6876A291": {"barcode": "32656 AGL IP7_86 and IP5_400 (TCTACTAC-GTTAGCCG)"},
                    "SOA6876A292": {"barcode": "25038 AGL IP7_66 and IP5_462 (ACCTTATT-AGGCGTCG)"},
                    "SOA6876A293": {"barcode": "4290 AGL IP7_12 and IP5_450 (ACTGCAAG-AATAAGGT)"},
                    "SOA6876A294": {"barcode": "6234 AGL IP7_17 and IP5_474 (TCGTTCGA-CCGCTAAC)"},
                    "SOA6876A295": {"barcode": "38188 AGL IP7_100 and IP5_556 (CGCAAGCT-GAGCCTCC)"},
                    "SOA6876A296": {"barcode": "62326 AGL IP7_163 and IP5_502 (GTTCAATA-GGAGCCAA)"},
                    "SOA6876A297": {"barcode": "72319 AGL IP7_189 and IP5_511 (CCTTCAGG-CGCCAGTT)"},
                    "SOA6876A298": {"barcode": "49340 AGL IP7_129 and IP5_572 (CTTCGTTA-CTTGAGTT)"},
                    "SOA6876A299": {"barcode": "44672 AGL IP7_117 and IP5_512 (CTGGATAA-GCCTTGCT)"},
                    "SOA6876A300": {"barcode": "66624 AGL IP7_174 and IP5_576 (GATCTTCC-TTGCGGAC)"},
                    "SOA6876A301": {"barcode": "57393 AGL IP7_150 and IP5_561 (AGGCAAGG-ATTAATCC)"},
                    "SOA6876A302": {"barcode": "50791 AGL IP7_133 and IP5_487 (CGGAATCA-TGCTTCGC)"},
                    "SOA6876A303": {"barcode": "47410 AGL IP7_124 and IP5_562 (TGACGAAC-AATGCAAT)"},
                    "SOA6876A304": {"barcode": "6999 AGL IP7_19 and IP5_471 (TCCTCCGC-CTAGGACC)"},
                    "SOA6876A305": {"barcode": "13844 AGL IP7_37 and IP5_404 (ACTCCGCG-GTCGCGAA)"},
                    "SOA6876A306": {"barcode": "7688 AGL IP7_21 and IP5_392 (CTCTGATG-CAATGGAT)"},
                    "SOA6876A307": {"barcode": "21130 AGL IP7_56 and IP5_394 (GCTCTGCT-AGGAGGCC)"},
                    "SOA6876A308": {"barcode": "55479 AGL IP7_145 and IP5_567 (TCAGGCGA-GATAAGTA)"},
                    "SOA6876A309": {"barcode": "54249 AGL IP7_142 and IP5_489 (ACTATATA-ACTTACGG)"},
                    "SOA6876A310": {"barcode": "46568 AGL IP7_122 and IP5_488 (GAACCGTT-AATCCGTC)"},
                    "SOA6876A311": {"barcode": "44266 AGL IP7_116 and IP5_490 (GGCAGCCG-AAGGTTAT)"},
                    "SOA6876A312": {"barcode": "53531 AGL IP7_140 and IP5_539 (AGCGGCAA-AGCAGGAG)"},
                    "SOA6876A313": {"barcode": "42791 AGL IP7_112 and IP5_551 (TGACTCAA-CGGAACTT)"},
                    "SOA6876A314": {"barcode": "49644 AGL IP7_130 and IP5_492 (GCATGGCG-CGACGTTA)"},
                    "SOA6876A315": {"barcode": "55078 AGL IP7_144 and IP5_550 (AAGTTGGA-CGACGGCT)"},
                    "SOA6876A316": {"barcode": "25797 AGL IP7_68 and IP5_453 (CGACGTAG-TGAGATCA)"},
                    "SOA6876A317": {"barcode": "8879 AGL IP7_24 and IP5_431 (TCCGTATA-ATGCTTCT)"},
                    "SOA6876A318": {"barcode": "1950 AGL IP7_6 and IP5_414 (CCATATAG-CGGTTCCA)"},
                    "SOA6876A319": {"barcode": "30776 AGL IP7_81 and IP5_440 (CTGCTCGT-AGCAGAGC)"},
                },
            ),  # custom barcode
            (
                "ASF_A05136-P27",
                {
                    "SKO6875A940": {"barcode": "13869 AGL IP7_37 and IP5_429 (ACTCCGCG-TAGTCGTT)"},
                },
            ),  # custom barcode
            (
                "20240625_1734_2F_PAW20497_d0c3cbb5",
                {
                    "KAN6921A20": {"barcode": ""},
                },
            ),  # regular barcode
        ],
    )
    def test_get_sample_custom_barcode_from_runid_isvalid(self, api, run_id, expected_dict):
        """
        Pass real run_id and test expected values in the dictionary output
        """

        # Test
        barcode = api.get_sample_custom_barcode_from_runid(run_id)

        # Assert
        assert barcode == expected_dict

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
                "ASF_A05136-P27",
                {
                    "SKO6875A940": {
                        "sample_name": "L12120",
                        "group": "skoglundp",
                        "user": "pontus.skoglund",
                        "project_id": "PM24043",
                        "project_limsid": "SKO6875",
                        "project_type": "Other",
                        "reference_genome": "Other",
                        "data_analysis_type": "None",
                        "barcode": "13869 AGL IP7_37 and IP5_429 (ACTCCGCG-TAGTCGTT)",
                    },
                },
            ),  # Illumina, custom barcode
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
                        "barcode": "",
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
        print(merged_dict)

        # Assert
        assert merged_dict == expected_dict
