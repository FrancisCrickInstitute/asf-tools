import pytest
from asf_tools.api.clarity.clarity_lims import ClarityLims

# @pytest.mark.parametrize("runid,expected", [
#     ("20240417_1729_1C_PAW45723_05bb74c5", 1)
# ])
def test_get_artifacts_from_runid_valid(self):
    # Setup
    api = ClarityLims()
    runid = "20240417_1729_1C_PAW45723_05bb74c5"
    expected = 1

    # Test
    artifacts = api.get_artifacts_from_runid(runid)

    # Assert
    assert len(artifacts) == expected