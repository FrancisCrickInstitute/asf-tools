# Illumina samplesheet generation

The `runs_san_samplesheet.pl` script automates the generation of sample sheets, updates database logs, and handles sequencing data processing errors. 
The script has 2 main functionalities: `run_info` or `scan_for_samplesheets`. The former interacts with Clarity and with the `RunInfo.xml` file to extract sample information as required. The latter checks the mysql database for new runs and generates a samplesheet for each new run by submitting the `create_illumina_samplesheet.pl` script.  

## Create_illumina_samplesheet

The `create_illumina_samplesheet` creates a samplesheet with a [Data] section followed by a table with this header: “Lane,Sample_ID,User_Sample_Name,index,index2,Index_ID,Sample_Project,Project_limsid,User,Lab,ReferenceGenome,DataAnalysisType“.
This information is extracted from the Clarity database.
