"""
Clarity API Tests
"""

import unittest
import pytest
from tests.mocks.mock_clarity_lims import MockClarityLims

from asf_tools.api.clarity.clarity_lims import ClarityLims

MOCK_API_DATA_DIR = "tests/data/api/clarity/mock_data"


class TestClarity(unittest.TestCase):
    """Class for testing the clarity api wrapper"""

    def setUp(self):
        self.api = MockClarityLims(MOCK_API_DATA_DIR)

    @pytest.mark.only_run_with_direct_target
    def test_mock_clarity_generate_data(self):
        """
        Generates a new test data set from the api
        """

        MockClarityLims.generate_test_data(MOCK_API_DATA_DIR)

    @pytest.mark.only_run_with_direct_target
    def test_clarity_api(self):
        lims = ClarityLims()

        run_id = "20240417_1729_1C_PAW45723_05bb74c5"
        run_container = lims.get_containers(name=run_id)[0]
        print("Container")
        print(f"Name: {run_container.name}")
        print(f"Type: {run_container.type}")
        print(f"Wells: {run_container.occupied_wells}")
        print(f"Placements: {run_container.placements}")
        print(f"UDF: {run_container.udf}")
        print(f"UDT: {run_container.udt}")
        print(f"State: {run_container.state}")

        # projects = lims.get_projects(name="RN24071")
        # print(projects)

        raise ValueError


# my $placements = {};
# my $in = uri_to_xml('https://asf-claritylims.thecrick.org/api/v2/containers?name='.$flowcell);

# if ( ref @{$in->{'container'}}[0] ne 'HASH' ) {
# 	say 'no container';
# 	exit;
# };

# my $container_loc = @{$in->{'container'}}[0];
# my $container = uri_to_xml(@{$container_loc->{'uri'}}[0]);
# for my $placement_loc (@{$container->{'placement'}}) {  ## take this 0 away else you're only processing one lane
# 	$placements->{@{$placement_loc->{'value'}}[0]}->{'loaded'} = @{$placement_loc->{'uri'}}[0];
# };
# for my $keys (keys %{$placements} ) {
# 	my $mpx = uri_to_xml($placements->{$keys}->{'loaded'});
# 	$placements->{$keys}->{'mpx'} = @{$mpx->{'name'}}[0];
# 	say 'getting mpx placements: '.$keys;
# 	for my $samples (@{$mpx->{'sample'}}) {
# 		$placements->{$keys}->{'samples'}->{ @{$samples->{'limsid'}}[0] }->{'uri'} = @{$samples->{'uri'}}[0];
# 	};
# 	my $parent_process_loc = @{$mpx->{'parent-process'}}[0];
# 	$placements->{$keys}->{'parent-process'}->{'limsid'}->{@{$parent_process_loc->{'limsid'}}[0]}->{'uri'} = @{$parent_process_loc->{'uri'}}[0];
# };
# # say Dumper $placements;
# for my $keys (keys %{$placements} ) {
# 	say 'getting processes: '.$keys;
# 	for my $limsid (keys %{$placements->{$keys}->{'parent-process'}->{'limsid'} } ) {
# 		get_inputs($keys,$placements->{$keys}->{'parent-process'}->{'limsid'}->{$limsid}->{'uri'});
# 	};
# };

# for my $keys (keys %{$placements} ) {
# 	for my $samples (keys %{$placements->{$keys}->{'samples'}} ) {
# 		if (not defined $placements->{$keys}->{'samples'}->{$samples}->{'reference-genome'}) {
# 			$placements->{$keys}->{'samples'}->{$samples}->{'reference-genome'} = $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'reference-genome'};
# 		} else {};
# 		if (not defined $placements->{$keys}->{'samples'}->{$samples}->{'user'}) {
# 			$placements->{$keys}->{'samples'}->{$samples}->{'user'} = $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'user'};
# 		} else {};
# 		if (not defined $placements->{$keys}->{'samples'}->{$samples}->{'lab'}) {
# 			$placements->{$keys}->{'samples'}->{$samples}->{'lab'} = $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'lab'};
# 		} else {};
# 		$placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'name'} = 'unknown';
# 		$placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'name'} =  $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'name'};
# 		$placements->{$keys}->{'samples'}->{$samples}->{'type'} = $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'type'};
# 		$placements->{$keys}->{'samples'}->{$samples}->{'analysis'} = $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'analysis'};	
# 		$placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'limsid'} =  $projects->{ $placements->{$keys}->{'samples'}->{$samples}->{'project'}->{'uri'} }->{'limsid'};

# 	};
# };
