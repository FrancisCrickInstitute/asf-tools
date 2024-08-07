# i'll write the functionality function then split it into a class with subfunctions

# i need to parse through runinfo and save this info in a dict
# dict would eventually be saved as a file or info added to a database

# input: input_path + runinfo

import xmltodict

class IlluminaUtils:

    def runinfo_parser(self, runinfo_file) -> dict:
        #info to extract:
        # run
        # reads
        # machine
        # platform

        # my $insert = {'SampleSheet_Trigger' => 'N', 'SampleSheet_TimeStamp' => $sst, 'SampleSheet' => $ss, 'Run_Date' => $date->strftime('%Y-%m-%d'), 'Date' => DateTime->now( time_zone => 'Europe/London' ), 'Run_ID' => @{$run_info->{'Id'}}[0], 'Platform' => @{$run_info->{'Instrument'}}[0], 'End_Type' => $end_type, 'Instrument' => $machine}

        with open(runinfo_file, 'r', encoding="utf-8") as runinfo_file:
            runinfo_file_content = runinfo_file.read()

        runinfo_dict = xmltodict.parse(runinfo_file_content)



        return runinfo_dict

