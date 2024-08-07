# i'll write the functionality function then split it into a class with subfunctions

# i need to parse through runinfo and save this info in a dict
# dict would eventually be saved as a file or info added to a database

import re
from datetime import datetime
import xmltodict

class IlluminaUtils:

    def runinfo_xml_to_dict(self, runinfo_file) -> dict:
        with open(runinfo_file, 'r', encoding="utf-8") as runinfo_file:
            runinfo_file_content = runinfo_file.read()
            # return error if file==empty

        full_runinfo_dict = xmltodict.parse(runinfo_file_content)
        return full_runinfo_dict

    def filter_runinfo(self, runinfo_dict: dict) -> dict:

        # Extract info from the dictionary as required
        run_id = runinfo_dict["RunInfo"]["Run"]["@Id"]
        instrument = runinfo_dict["RunInfo"]["Run"]["Instrument"]

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
        # print(runinfo_dict)
        return runinfo_dict

    def filter_readinfo(self, runinfo_dict: dict) -> dict:

        run_id = runinfo_dict["RunInfo"]["Run"]["@Id"] # returns a string
        reads_fullinfo = runinfo_dict["RunInfo"]["Run"]["Reads"] # returns a dict

        # Extract single or paired end info for each read
        end_type_count = 0
        read_data = []
        for read in reads_fullinfo['Read']:
            number = read['@Number']
            num_cycles = read['@NumCycles']
            is_indexed_read = read['@IsIndexedRead']

            if is_indexed_read == 'N':
                # read_data[f'Read {number}'] = f'{num_cycles} Seq'
                read_data.append({"read": f'Read {number}', "num_cycles": f'{num_cycles} Seq'})
                end_type_count += 1
            elif is_indexed_read == 'Y':
                # read_data[f'Read {number}'] = f'{num_cycles} Ind'
                read_data.append({"read": f'Read {number}', "num_cycles": f'{num_cycles} Seq'})

        end_type = "SR"
        if end_type_count > 1:
            end_type = "PE"

        # Collect the extracted info in a single dictionary
        readinfo_dict = {}
        readinfo_dict["run_id"] = run_id
        readinfo_dict["end_type"] = end_type
        readinfo_dict["reads"] = read_data
        # print(readinfo_dict)

        return readinfo_dict
    
    def merge_runinfo_dict_fromfile(self, runinfo_file) -> dict:
        original_dict = self.runinfo_xml_to_dict(runinfo_file)
        filtered_dict = self.filter_runinfo(original_dict)
        reads_dict = self.filter_readinfo(original_dict)

        merged_dict = filtered_dict
        # for key, value in reads_dict.items():
        #     for sub_key, sub_value in value.items():
        #         if key in merged_dict:
        #             merged_dict[key][sub_key] = sub_value
        # print(merged_dict)

        return merged_dict

# my $insert = {'SampleSheet_Trigger' => 'N', 'SampleSheet_TimeStamp' => $sst, 'SampleSheet' => $ss, 'End_Type' => $end_type}