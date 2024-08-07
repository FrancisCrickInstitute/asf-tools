# i'll write the functionality function then split it into a class with subfunctions

# i need to parse through runinfo and save this info in a dict
# dict would eventually be saved as a file or info added to a database

import re
from datetime import datetime
import xmltodict

class IlluminaUtils:

    def runinfo_parser(self, runinfo_file) -> dict:

        # my $insert = {'SampleSheet_Trigger' => 'N', 'SampleSheet_TimeStamp' => $sst, 'SampleSheet' => $ss, 'Run_Date' => $date->strftime('%Y-%m-%d'), 'Date' => DateTime->now( time_zone => 'Europe/London' ), 'End_Type' => $end_type}

        with open(runinfo_file, 'r', encoding="utf-8") as runinfo_file:
            runinfo_file_content = runinfo_file.read()

        full_runinfo_dict = xmltodict.parse(runinfo_file_content)

        run_id = full_runinfo_dict["RunInfo"]["Run"]["@Id"]
        instrument = full_runinfo_dict["RunInfo"]["Run"]["Instrument"]

        machine_mapping = {
            '^M': 'MiSeq',
            '^K': 'HiSeq 4000',
            '^D': 'HiSeq 2500',
            '^N': 'NextSeq',
            '^A': 'NovaSeq',
            '^LH': 'NovaSeqX'
        }

        for pattern, machine_name in machine_mapping.items():
            if re.match(pattern, instrument):
                machine = machine_name

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        runinfo_dict = {"current_date":current_datetime, "run_id": run_id, "instrument": instrument, "machine": machine}
        print(runinfo_dict)
        return runinfo_dict

