"""
Clarity helper API Tests
"""

# pylint: disable=missing-function-docstring,missing-class-docstring,no-member

import os

import pytest
import xmltodict
from assertpy import assert_that
from requests.exceptions import ConnectionError, HTTPError  # pylint: disable=redefined-builtin

from asf_tools.api.clarity.models import Stub
from tests.mocks.clarity_helper_lims_mock import ClarityHelperLimsMock


API_TEST_DATA = "tests/data/api/clarity"


# Create class level mock API
@pytest.fixture(scope="class", autouse=True)
def mock_clarity_api(request):
    data_file_path = os.path.join(API_TEST_DATA, "mock_data", "helper-data.pkl")
    api = ClarityHelperLimsMock(baseuri="https://asf-claritylims.thecrick.org")
    api.load_tracked_requests(data_file_path)
    request.cls.api = api
    request.addfinalizer(lambda: api.save_tracked_requests(data_file_path))
    yield api


class TestClarityHelperLims:
    def test_clarity_helper_get_artifacts_from_runid_isnone(self):
        # Test and Assert
        assert_that(self.api.get_artifacts_from_runid).raises(ValueError).when_called_with(None)

    def test_clarity_helper_get_artifacts_from_runid_isinvalid(self):
        # Test and Assert
        assert_that(self.api.get_artifacts_from_runid).raises(KeyError).when_called_with("fake_runid")

    def test_clarity_helper_get_lane_from_runid_isnone(self):
        # Test and Assert
        assert_that(self.api.get_lane_from_runid).raises(ValueError).when_called_with(None)

    def test_clarity_helper_get_lane_from_runid_isinvalid(self):
        # Test and Assert
        assert_that(self.api.get_lane_from_runid).raises(KeyError).when_called_with("Fake_runid")

    def test_clarity_helper_get_samples_from_artifacts_isnone(self):
        # Test and Assert
        assert_that(self.api.get_samples_from_artifacts).raises(ValueError).when_called_with(None)

    def test_clarity_helper_get_samples_from_artifacts_isinvalid(self):
        # Setup
        artifacts_list = [Stub(id="TestID", uri="https://asf-claritylims.thecrick.org/api/v2/artifacts/TEST", name=None, limsid="TestID")]

        # Test and Assert
        with pytest.raises(Exception) as excinfo:
            self.api.get_samples_from_artifacts(artifacts_list)
        assert isinstance(excinfo.value, (ConnectionError, HTTPError))

    def test_clarity_helper_get_check_sample_dropoff_isnone(self):
        # Test and assert
        assert_that(self.api.check_sample_dropoff_info(None)).is_none()

    def test_clarity_helper_get_check_sample_dropoff_isvalid(self):
        # Set up
        sample_1 = "GOL5512A6973"  # drop-off sample
        expected_dict_1 = {
            "Drop-Off Amplicon Size (bp)": "114",
            "Drop-Off Budget Code": "CC2063",
            "Drop-Off Lab Name": "saterialea",
            "Drop-Off Number of Replicates Requested": "2",
            "Drop-Off Researcher Name": "Silvia Haase",
        }

        sample_2 = "KAN6921A20"  # regular sample
        expected_dict_2 = {}

        # Test
        get_info_1 = self.api.check_sample_dropoff_info(sample_1)
        get_info_2 = self.api.check_sample_dropoff_info(sample_2)

        # Assert
        assert_that(get_info_1).is_equal_to(expected_dict_1)
        assert_that(get_info_2).is_equal_to(expected_dict_2)

    def test_clarity_helper_get_sample_info_isnone(self):
        # Test and assert
        assert_that(self.api.get_sample_info(None)).is_none()

    def test_clarity_helper_get_barcode_from_reagenttypes_isnone(self):
        # Test and assert
        assert_that(self.api.get_barcode_from_reagenttypes(None)).is_none()

    def test_clarity_helper_get_barcode_from_reagenttypes_isvalid(self):
        # Setup
        barcode = "N701-N501 (TAAGGCGA-TAGATCGC)"
        results_barcode = "TAAGGCGA-TAGATCGC"

        # Test and assert
        assert_that(self.api.get_barcode_from_reagenttypes(barcode)).is_equal_to(results_barcode)

    def test_clarity_helper_get_sample_barcode_from_runid_isnone(self):
        # Test and Assert
        assert_that(self.api.get_sample_barcode_from_runid).raises(ValueError).when_called_with(None)

    def test_clarity_helper_reformat_barcode_to_index_isvalid(self):
        # Setup
        sample_info = {
            "sample1": {"barcode": None},
            "sample2": {"barcode": "First Kit (GeneX-YGeneY)"},
            "sample3": {"project": "Project Info", "barcode": "Second Kit (CTTGTGCT-ACATACAC)"},
            "sample4": {"barcode": "Random Kit (SingleIndex)"},
            "sample5": {"info": "No barcode in dict"},
        }
        expected = {
            "sample2": {"index": "GeneX", "index2": "YGeneY"},
            "sample3": {"index": "CTTGTGCT", "index2": "ACATACAC"},
            "sample4": {"index": "SingleIndex", "index2": ""},
        }

        # Test
        result = self.api.reformat_barcode_to_index(sample_info)

        # Assert
        assert_that(result).is_equal_to(expected)

    def test_clarity_helper_collect_samplesheet_info_isnone(self):
        # Test and Assert
        assert_that(self.api.collect_samplesheet_info).raises(ValueError).when_called_with(None)

    def test_clarity_helper_get_barcode_from_reagenttypes_isinvalid(self, caplog):
        # Setup
        barcode = "fake_barcode"

        # Test
        results = self.api.get_barcode_from_reagenttypes(barcode)  # Call the function that raises a warning

        # Assert
        assert_that(results).is_equal_to(barcode)
        assert_that(caplog.text).contains("WARNING")

    def test_clarity_helper_get_barcode_from_reagenttypes_warning_1(self, caplog, monkeypatch):
        # Setup
        barcode = "fake_barcode"
        custom_xml = "<xml>mock_reagent_types</xml>"
        custom_xml_dict = {}
        monkeypatch.setattr(self.api, "get_with_uri", lambda uri, *args, **kwargs: custom_xml)
        monkeypatch.setattr(xmltodict, "parse", lambda uri, *args, **kwargs: custom_xml_dict)

        # Test
        results = self.api.get_barcode_from_reagenttypes(barcode)

        # Assert
        assert_that(results).is_equal_to(barcode)
        assert_that(caplog.text).contains("WARNING")

    def test_clarity_helper_get_barcode_from_reagenttypes_warning_2(self, caplog, monkeypatch):
        # Setup
        barcode = "fake_barcode"
        custom_xml = "<xml>mock_reagent_types</xml>"
        custom_xml_dict = {"rtp:reagent-types": {"reagent-type": {}}}
        monkeypatch.setattr(self.api, "get_with_uri", lambda uri, *args, **kwargs: custom_xml)
        monkeypatch.setattr(xmltodict, "parse", lambda uri, *args, **kwargs: custom_xml_dict)

        # Test
        results = self.api.get_barcode_from_reagenttypes(barcode)

        # Assert
        assert_that(results).is_equal_to(barcode)
        assert_that(caplog.text).contains("WARNING")

    def test_clarity_helper_get_barcode_from_reagenttypes_warning_3(self, caplog, monkeypatch):
        # Setup
        barcode = "fake_barcode"
        custom_xml = ["<xml>mock_reagent_types</xml>", "<xml>mock_reagent_type_details</xml>"]
        custom_xml_dict = [{"rtp:reagent-types": {"reagent-type": {"uri": "mock_uri"}}}, {"rtp:reagent-type": {}}]
        monkeypatch.setattr(self.api, "get_with_uri", lambda uri, *args, **kwargs: custom_xml.pop(0))
        monkeypatch.setattr(xmltodict, "parse", lambda uri, *args, **kwargs: custom_xml_dict.pop(0))

        # Test
        results = self.api.get_barcode_from_reagenttypes(barcode)

        # Assert
        assert_that(results).is_equal_to(barcode)
        assert_that(caplog.text).contains("WARNING")

    def test_clarity_helper_get_barcode_from_reagenttypes_warning_4(self, caplog, monkeypatch):
        # Setup
        barcode = "fake_barcode"
        custom_xml = ["<xml>mock_reagent_types</xml>", "<xml>mock_reagent_type_details</xml>"]
        custom_xml_dict = [
            {"rtp:reagent-types": {"reagent-type": {"uri": "mock_uri"}}},
            {"rtp:reagent-type": {"special-type": {"attribute": {"name": "InvalidName"}}}},
        ]
        monkeypatch.setattr(self.api, "get_with_uri", lambda uri, *args, **kwargs: custom_xml.pop(0))
        monkeypatch.setattr(xmltodict, "parse", lambda uri, *args, **kwargs: custom_xml_dict.pop(0))

        # Test
        results = self.api.get_barcode_from_reagenttypes(barcode)

        # Assert
        assert_that(results).is_equal_to(barcode)
        assert_that(caplog.text).contains("WARNING")

    def test_clarity_helper_reformat_barcode_to_index_novalid_barcodes(self, caplog):
        # Setup
        sample_info = {"sample1": {"barcode": None}, "sample2": {"barcode": ""}, "sample3": {"user": "No user", "barcode": "No Barcode"}}
        expected = {}

        # Test
        results = self.api.reformat_barcode_to_index(sample_info)  # Call the function that raises a warning

        # Assert
        assert_that(results).is_equal_to(expected)
        assert_that(caplog.text).contains("WARNING")

    @pytest.mark.parametrize("runid,expected", [("20240417_1729_1C_PAW45723_05bb74c5", 1), ("20240625_1734_2F_PAW20497_d0c3cbb5", 1)])
    def test_clarity_helper_get_artifacts_from_runid_valid(self, runid, expected):
        """
        Pass real run IDs and test expected number of artifacts back
        """

        # Test
        artifacts = self.api.get_artifacts_from_runid(runid)

        # Assert
        assert len(artifacts) == expected

    @pytest.mark.parametrize(
        "run_id,expected",
        [
            (
                "HWNT7BBXY",
                {
                    "HWNT7BBXY_1": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373229",
                        "lane": "1",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_2": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373230",
                        "lane": "2",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_3": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373231",
                        "lane": "3",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_4": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373232",
                        "lane": "4",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_5": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373233",
                        "lane": "5",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_6": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373234",
                        "lane": "6",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_7": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373235",
                        "lane": "7",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                    "HWNT7BBXY_8": {
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/2-8373236",
                        "lane": "8",
                        "samples": [
                            "TLG66A2839",
                            "TLG66A2840",
                            "TLG66A2841",
                            "TLG66A2842",
                            "TLG66A2843",
                            "TLG66A2844",
                            "TLG66A2845",
                            "TLG66A2848",
                            "TLG66A2849",
                        ],
                    },
                },
            ),
            (
                "ASF_A05136-P27",
                {
                    "ASF_A05136-P27_1": {
                        "samples": ["SKO6875A940"],
                        "artifact_uri": "https://asf-claritylims.thecrick.org/api/v2/artifacts/SKO6875A940PA1",
                        "lane": "1",
                    },
                },
            ),
        ],
    )
    def test_clarity_helper_get_lane_from_runid_isvalid(self, run_id, expected):
        # Test and assert
        assert_that(self.api.get_lane_from_runid(run_id)).is_equal_to(expected)

    @pytest.mark.parametrize("run_id,expected_sample_quantity", [("B_04-0004-S6_DT", 1), ("462-24_MPX-seq", 4)])  # Illumina  # ONT
    def test_clarity_helper_get_samples_from_artifacts_isvalid(self, run_id, expected_sample_quantity):
        """
        Pass real artifact IDs and test expected number of samples back
        """

        # Set up
        artifact = self.api.get_artifacts(name=run_id)

        # Test
        get_samples = self.api.get_samples_from_artifacts(artifact)

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
                        "user": "clare.puttick",
                        "project_id": "DN24086",
                        "project_limsid": "KAN6921",
                        "project_type": "WGS",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "None",
                        "library_type": "ONT DNA Ligation",
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
                        "library_type": "NEBNext_Low_Input_w_NEB_Ultra_II_FS",
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
                        "library_type": "Premade",
                    }
                },
            ),
            (
                "GOL5512A6973",
                {
                    "GOL5512A6973": {
                        "sample_name": "CpPRO_input",
                        "group": "saterialea",
                        "user": "silvia.haase",
                        "project_id": "DN19023",
                        "project_limsid": "GOL5512",
                        "project_type": "Amplicons",
                        "reference_genome": "Other",
                        "data_analysis_type": "None",
                        "library_type": "Index PCR",
                    }
                },
            ),  # Illumina drop off
        ],
    )
    def test_clarity_helper_get_sample_info_isvalid(self, sample_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """

        # Set up
        sample = self.api.get_samples(search_id=sample_id)

        # Test and assert
        assert_that(self.api.get_sample_info(sample.id)).is_equal_to(expected_dict)

    @pytest.mark.parametrize(
        "sample_id,expected_dict",
        [
            (
                "201C-2076956",
                {
                    "201C-2076956": {
                        "sample_name": "No_Template_Control",
                        "group": "sequencing",
                        "user": "ashley.fowler",
                        "project_id": None,
                        "project_limsid": None,
                        "project_type": None,
                        "reference_genome": None,
                        "data_analysis_type": None,
                        "library_type": None,
                    }
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_info_project_notexists(self, sample_id, expected_dict):
        """
        Pass real sample IDs and test expected values in the dictionary output
        """

        # Set up
        sample = self.api.get_samples(search_id=sample_id)

        # Test and Assert
        assert_that(self.api.get_sample_info(sample.id)).is_equal_to(expected_dict)

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
    def test_clarity_helper_collect_sample_info_from_runid(self, runid, expected_sample_quantity):
        """
        Pass real run IDs and test expected number of samples stored in the dictionary output
        """

        # Test
        sample_dict = self.api.collect_sample_info_from_runid(runid)

        # Assert
        assert len(sample_dict) == expected_sample_quantity

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {"barcode": "AAGAAAGTTGTCGGTGTCTTTGTG"},
                    "VIV6902A2": {"barcode": "TCGATTCCGTTTGTAGTCGTCTGT"},
                    "VIV6902A3": {"barcode": "GAGTCTTGTGTCCCAGTTACCAGG"},
                    "VIV6902A4": {"barcode": "TTCGGATTCTATCGTGTTTCCCTA"},
                },
            ),  # ONT
            ("20240625_1734_2F_PAW20497_d0c3cbb5", {}),
            (
                "20240807_1248_P2S-02348-A_PAW31464_90cccf6c",
                {
                    "SWA6667A7": {"barcode": "AAGAAAGTTGTCGGTGTCTTTGTG"},
                    "SWA6667A8": {"barcode": "TCGATTCCGTTTGTAGTCGTCTGT"},
                    "SWA6667A37": {"barcode": "GAGTCTTGTGTCCCAGTTACCAGG"},
                    "SWA6667A38": {"barcode": "TTCGGATTCTATCGTGTTTCCCTA"},
                    "SWA6667A39": {"barcode": "CTTGTCCAGGGTTTGTGTAACCTT"},
                    "SWA6667A41": {"barcode": "TTCTCGCAAAGGCAGAAAGTAGTC"},
                    "201C-2072202": {"barcode": "GTGTTACCGTGGGAATGAATCCTT"},
                },
            ),
        ],
    )
    def test_clarity_helper_get_sample_barcode_from_runid_isvalid(self, run_id, expected_dict):
        # Test and assert
        assert_that(self.api.get_sample_barcode_from_runid(run_id)).is_equal_to(expected_dict)

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "22G2JFLT4",
                {
                    "SOA6876A276": {"barcode": "AGACCAAT-AACTCCGG"},
                    "SOA6876A277": {"barcode": "ACCAAGAT-ATTGGTCT"},
                    "SOA6876A278": {"barcode": "ACTCTTGG-AGCTCCAA"},
                    "SOA6876A279": {"barcode": "CGTTCGCT-AGCGAACG"},
                    "SOA6876A280": {"barcode": "CGTAGATC-CAATTGCA"},
                    "SOA6876A281": {"barcode": "TGGTCCTG-TAACGAAG"},
                    "SOA6876A282": {"barcode": "AGCAAGGC-GCCGTCCG"},
                    "SOA6876A283": {"barcode": "TGGTTGAC-TCTGACTG"},
                    "SOA6876A284": {"barcode": "TGCTCTTC-AGGTCGGA"},
                    "SOA6876A285": {"barcode": "ATAATGGT-AGGTAGTT"},
                    "SOA6876A286": {"barcode": "TCAGTTAA-TTAACTGA"},
                    "SOA6876A287": {"barcode": "CCGGCGAC-TTCTAATG"},
                    "SOA6876A288": {"barcode": "GGCTTGAA-TTGACTAT"},
                    "SOA6876A289": {"barcode": "GGCCTCCT-AATCGCAT"},
                    "SOA6876A290": {"barcode": "CTATTCAT-AAGAGCGC"},
                    "SOA6876A291": {"barcode": "TCTACTAC-GTTAGCCG"},
                    "SOA6876A292": {"barcode": "ACCTTATT-AGGCGTCG"},
                    "SOA6876A293": {"barcode": "ACTGCAAG-AATAAGGT"},
                    "SOA6876A294": {"barcode": "TCGTTCGA-CCGCTAAC"},
                    "SOA6876A295": {"barcode": "CGCAAGCT-GAGCCTCC"},
                    "SOA6876A296": {"barcode": "GTTCAATA-GGAGCCAA"},
                    "SOA6876A297": {"barcode": "CCTTCAGG-CGCCAGTT"},
                    "SOA6876A298": {"barcode": "CTTCGTTA-CTTGAGTT"},
                    "SOA6876A299": {"barcode": "CTGGATAA-GCCTTGCT"},
                    "SOA6876A300": {"barcode": "GATCTTCC-TTGCGGAC"},
                    "SOA6876A301": {"barcode": "AGGCAAGG-ATTAATCC"},
                    "SOA6876A302": {"barcode": "CGGAATCA-TGCTTCGC"},
                    "SOA6876A303": {"barcode": "TGACGAAC-AATGCAAT"},
                    "SOA6876A304": {"barcode": "TCCTCCGC-CTAGGACC"},
                    "SOA6876A305": {"barcode": "ACTCCGCG-GTCGCGAA"},
                    "SOA6876A306": {"barcode": "CTCTGATG-CAATGGAT"},
                    "SOA6876A307": {"barcode": "GCTCTGCT-AGGAGGCC"},
                    "SOA6876A308": {"barcode": "TCAGGCGA-GATAAGTA"},
                    "SOA6876A309": {"barcode": "ACTATATA-ACTTACGG"},
                    "SOA6876A310": {"barcode": "GAACCGTT-AATCCGTC"},
                    "SOA6876A311": {"barcode": "GGCAGCCG-AAGGTTAT"},
                    "SOA6876A312": {"barcode": "AGCGGCAA-AGCAGGAG"},
                    "SOA6876A313": {"barcode": "TGACTCAA-CGGAACTT"},
                    "SOA6876A314": {"barcode": "GCATGGCG-CGACGTTA"},
                    "SOA6876A315": {"barcode": "AAGTTGGA-CGACGGCT"},
                    "SOA6876A316": {"barcode": "CGACGTAG-TGAGATCA"},
                    "SOA6876A317": {"barcode": "TCCGTATA-ATGCTTCT"},
                    "SOA6876A318": {"barcode": "CCATATAG-CGGTTCCA"},
                    "SOA6876A319": {"barcode": "CTGCTCGT-AGCAGAGC"},
                },
            ),  # custom barcode
            (
                "ASF_A05136-P27",
                {
                    "SKO6875A940": {"barcode": "ACTCCGCG-TAGTCGTT"},
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
    def test_get_sample_custom_barcode_from_runid_isvalid(self, run_id, expected_dict):
        # Test and assert
        assert_that(self.api.get_sample_custom_barcode_from_runid(run_id)).is_equal_to(expected_dict)

    @pytest.mark.parametrize("sample,expected_barcode", [("SKO6875A940", "ACTCCGCG-TAGTCGTT"), ("KAN6921A20", "")])  # Illumina  # ONT
    def test_clarity_helper_get_sample_custom_barcode_from_sampleid_isvalid(self, sample, expected_barcode):
        # Test and assert
        assert_that(self.api.get_sample_custom_barcode_from_sampleid(sample)).is_equal_to(expected_barcode)

    @pytest.mark.parametrize(
        "run_id,expected_dict",
        [
            (
                "20240417_1729_1C_PAW45723_05bb74c5",
                {
                    "VIV6902A1": {
                        "barcode": "AAGAAAGTTGTCGGTGTCTTTGTG",
                        "sample_name": "BR1_D0",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                    "VIV6902A2": {
                        "barcode": "TCGATTCCGTTTGTAGTCGTCTGT",
                        "sample_name": "BR1_D7",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                    "VIV6902A3": {
                        "barcode": "GAGTCTTGTGTCCCAGTTACCAGG",
                        "sample_name": "BR2_D0",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
                    },
                    "VIV6902A4": {
                        "barcode": "TTCGGATTCTATCGTGTTTCCCTA",
                        "sample_name": "BR2_D7",
                        "group": "vanwervenf",
                        "user": "claudia.vivori",
                        "project_id": "RN24071",
                        "project_limsid": "VIV6902",
                        "project_type": "Other",
                        "reference_genome": "Mus musculus",
                        "data_analysis_type": "None",
                        "library_type": "Oxford Nanopore",
                        "lanes": ["1"],
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
                        "barcode": "CTGAGCCA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "AGCCATGC",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "GTACGCAA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "AGTACAAG",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "ACATTGGC",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "ATTGAGGA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "GTCGTAGA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "AACGTGAT",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "CACTTCGA",
                        "library_type": "SureSelectXT Human All Exon V5plus",
                        "lanes": ["1", "2", "3", "4", "5", "6", "7", "8"],
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
                        "barcode": "ACTCCGCG-TAGTCGTT",
                        "library_type": "Premade",
                        "lanes": ["1"],
                    },
                },
            ),  # Illumina, custom barcode
            (
                "20240625_1734_2F_PAW20497_d0c3cbb5",
                {
                    "KAN6921A20": {
                        "sample_name": "99-005-0496_98-290_bp",
                        "group": "swantonc",
                        "user": "clare.puttick",
                        "project_id": "DN24086",
                        "project_limsid": "KAN6921",
                        "project_type": "WGS",
                        "reference_genome": "Homo sapiens",
                        "data_analysis_type": "None",
                        "barcode": "",
                        "library_type": "ONT DNA Ligation",
                        "lanes": ["1"],
                    }
                },
            ),  # ONT, no barcode info
        ],
    )
    def test_clarity_helper_collect_samplesheet_info_isvalid(self, run_id, expected_dict):
        # Test and assert
        assert_that(self.api.collect_samplesheet_info(run_id)).is_equal_to(expected_dict)

    @pytest.mark.parametrize(
        "project_id,expected_dict", [("KAN6921", {"Demux Pipeline Params": {"output_raw": "True", "output_bam": "True"}}), ("TLG66", {})]
    )
    def test_clarity_helper_get_pipeline_params_isvalid(self, project_id, expected_dict):
        # Set up
        pipeline_params_field_name = "pipeline params"
        sep_value = "="

        # Test
        results = self.api.get_pipeline_params(project_id, pipeline_params_field_name, sep_value)

        # Assert
        assert_that(results).is_equal_to(expected_dict)
