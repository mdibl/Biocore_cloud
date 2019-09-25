# -*- coding: utf-8 -*-
import subprocess as sp
from os.path import join,isfile,isdir,dirname,basename
import getopt,os,sys,re
#import io,json
from datetime import date,datetime

from biocore_project_dom import BiocoreProjectInfoDOM
import  global_m as gb_m
from  aws_datasync_dom import AwsDataSyncDOM

'''
Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: September 2019

'''
def get_header():
    header='''
****************** AWS S3 Data Migrations ***********************************************

The tool runs project-specific data migration from biocore file system to AWS S3 buckets.

*****************************************************************************************
    '''
    return header

def prog_usage():
    usage=get_header()
    
    usage+='''

 Usage: PROG [-h] -c path2/teamName/projectName/runID/cfgs/pipeline.cfg 
  OR
 Usage: PROG [-h] --cfg=path2/teamName/projectName/runID/cfgs/pipeline.cfg 

 Where:
     -h To show the usage
     -c path2runID/cfgs/pipeline.cfg or --cfg=path2runID/cfgs/pipeline.cfg  ... required, 
      
 What It Does: Uses the pipeline.cfg and the json template found in pipeline.cfg
               to migrate recursively project-specific data to the Amazon S3 file system

 Example: 
       python mig_local2s3.py  -c /data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562768838/cfgs/pipeline.cfg 
       OR
       python mig_local2s3.py  --cfg=/data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562768838/cfgs/pipeline.cfg 
 
 ASSUMPTIONS: 
       1) User has full permission on AWS S3 file system
       2) Both json template(template.json) and the pipeline.cfg have been generated under the same directory(cfgs)
       3) S3 bucket is mounted on server running this script
       4) Path to local S3 mount is /s3-data/biocore-data
       5) AWS CLI is installed on server running this script 
       6) The pipeline steps and standards followed as specified in our documentation
       7) Our file server bc-node02.mdibl.net is the designated server to run data migrations

The program will fail with error if anyone of the project's expected structures is missing or is invalid.

   '''
    print("%s"%(usage))

## Transfers data from local file system to S3 buckets
## using S3 sync utilities 
#
def transfer_data2s3(biocore_obj,datasync_obj,log,read_suffix):
    done_list=[]
    for biocore_path,s3_path in biocore_obj.s3_biocore_items_map.items():
        ##remove trailing back slash from path
        if biocore_path.endswith("/"):biocore_path=biocore_path[:-1]
        if s3_path.endswith("/"):s3_path=s3_path[:-1]
        reads_transfer=False
        target_token=None
        if isfile(biocore_path):
           s3_dir_base=dirname(s3_path)
           source_base=dirname(biocore_path)
           target_token=basename(biocore_path)
        else:
           s3_dir_base=s3_path
           source_base=biocore_path
        transfer_label=target_token
        if transfer_label is None: transfer_label=basename(biocore_path)
        s3_uri=biocore_obj.get_s3_uri(s3_dir_base)
        if s3_uri in done_list: continue
        if biocore_obj.project_reads_base in source_base:
            samples=biocore_obj.get_reads_list(read_suffix)
            s3_reads_list=[f for f in os.listdir(s3_dir_base) if isfile(join(s3_dir_base,f))]
            for sample,reads in samples.items():
                for read_file in reads:
                    if read_file.replace(".gz","") not in s3_reads_list:reads_transfer=True
 
        log.write("----------------------------\n")
        log.write("Transferring : %s \n"%(transfer_label))
        log.write("Source: %s\nDestination: %s\nS3 URI: %s\n"%(source_base,s3_dir_base,s3_uri))
        if biocore_obj.project_reads_base in source_base and reads_transfer is False:
            log.write("Skipping Reads Transfer to S3\n")
            print("Skipping Reads Transfer to S3\n")
        else: 
            log.write("Transfer started:%s\n"%( datetime.now()))
            cmd="aws s3 sync "+source_base+" "+s3_uri
            log_console=datasync_obj.s3_sync(source_base,s3_uri)
            print("Migrating: %s\nCMD:%s\n"%(transfer_label,cmd))
            log.write("Transfer logs:\n%s\n"%(log_console))
            log.write("Transfer ended:%s\n"%( datetime.now()))
        done_list.append(s3_uri)

## Expands sequence read files on S3 stporage as needed
#
def expand_reads(s3_reads_path):
    reads_files=[f for f in os.listdir(s3_reads_path) if isfile(join(s3_reads_path,f))]
    try:
        os.chdir(s3_reads_path)
        for read_file in reads_files:
            if ".gz" in read_file:
                log.write("----------------------------\n")
                log.write("Expanding : %s \n"%(read_file))
                log.write("Process started:%s\n"%( datetime.now()))
                cmd="gunzip "+read_file
                log_console=sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
                print("Expanding: %s\n"%(read_file))
                log.write("Process logs:\n%s\n"%(log_console))
                log.write("Process ended:%s\n"%( datetime.now()))
    except:pass

if __name__== "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:s:", ["help", "cfg=","suffix"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print("ERROR:%s" % (str(err) )) 
        prog_usage()
        sys.exit(1)
    #set program arguments
    pipeline_config=None
    log_file=None
    ##default value for reads file name suffix
    reads_suffix="fastq.gz"
    for o, a in opts:
        if o in ("-c", "--cfg"):pipeline_config = a
        elif o in ("-s","--suffix"):reads_suffix = a
        elif o in ("-h", "--help"):
            prog_usage()
            sys.exit()
        else:
            assert False, "unhandled option"
    if pipeline_config is None or not isfile(pipeline_config):
        msg="ERROR: pipeline.cfg missing"
        print("%s - Check %s"%(msg,pipeline_config))
        prog_usage()
        sys.exit()
  
    biocore_obj=BiocoreProjectInfoDOM(pipeline_config)
    datasync_obj=AwsDataSyncDOM(biocore_obj.aws_account_id,biocore_obj.aws_onprem_agent_id,biocore_obj.aws_onprem_agent_ip)

    if biocore_obj.project_design_file is None or  not isfile(biocore_obj.project_design_file) :
        print("ERROR: Exp design file missing - see path:%s"%(biocore_obj.project_design_file))
        sys.exit()
    if biocore_obj.project_cwl_script is None or not isfile(biocore_obj.project_cwl_script):
        print("ERROR: Exp cwl script file missing - see path:%s"%(biocore_obj.project_cwl_script))
        sys.exit()
    if biocore_obj.json_template is None or not isfile(biocore_obj.json_template):
        print("ERROR: Exp json template file(template.json) missing - see path:%s"%(biocore_obj.json_template))
        sys.exit()

    if not isdir(biocore_obj.project_reads_base):
        print("ERROR: Path to Reads files not a directory  - see path:%s"%(biocore_obj.project_reads_base))
        sys.exit()
    if not isdir(biocore_obj.biocore_log_base):
        print("ERROR: Log directory missing - see:%s"%(biocore_obj.biocore_log_base ))
        sys.exit()
    if not isdir(biocore_obj.bicore_pipelinejson_dir):
        print("ERROR: Json files base directory missing - see:%s"%(biocore_obj.bicore_pipelinejson_dir))
        sys.exit()
    if not isdir(biocore_obj.bicore_pipelinemeta_dir):
        print("ERROR: Pcf files base directory missing - see:%s"%(biocore_obj.bicore_pipelinemeta_dir))
        sys.exit()
    
    log_file=join(biocore_obj.biocore_log_base,basename(__file__)+".log")
    log=open(log_file,'w') 
    log.write("**********************************\n")
    log.write("Starting Data Migration to AWS S3 \n")
    log.write("**********************************\n")
    log.write("Date:%s\n"%( date.today()))
    log.write("\n")
    log.write("Team Name:%s\n"%(biocore_obj.project_team_id)) 
    log.write("Project ID:%s\n"%(biocore_obj.project_name)) 
    log.write("Project RunID:%s\n"%(biocore_obj.project_run_id))
    log.write("    Main Config File: %s\n"%(pipeline_config))
    log.write("    Json Template : %s\n"%(biocore_obj.json_template))
    log.write("Log file:%s\n"%(log_file))
    log.write("\n")
    ##Transfer data to cloud
    transfer_data2s3(biocore_obj,datasync_obj,log,reads_suffix)
    ## expand reads files if needed
    s3_reads_path=biocore_obj.get_s3_path(biocore_obj.scratch_reads_base)
    if not isdir(s3_reads_path):
        log.write("ERROR: Invalid path to reads - see %s\n"%(s3_reads_path))
    else: expand_reads(s3_reads_path)
    log.write("Program complete\n")
    ## transfer this runID base
    s3_results_base=biocore_obj.get_s3_path(biocore_obj.project_results_base)
    s3_uri=biocore_obj.get_s3_uri(s3_results_base)
    print("Transferring the results base directory \n")
    print("Source: %s\nDestination: %s\n\n"%(biocore_obj.project_results_base,s3_results_base))
    log_console=datasync_obj.s3_sync(biocore_obj.project_results_base,s3_uri)
    print("Transfer logs:\n%s\n---------------\n"%(log_console))
    print("Program complete.\nCheck the logs for errors:\n%s\n"%(log_file))
    sys.exit()
