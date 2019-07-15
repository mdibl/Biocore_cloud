# -*- coding: utf-8 -*-
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
Date: July 2019

'''
def get_header():
    header='''
****************** AWS EFS Software Migrations ***********************************************

The tool runs project-specific software packages migration from biocore file system to AWS EFS.

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
       python migrate_software2efs.py  -c /data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562768838/cfgs/pipeline.cfg 
       OR
       python migrate_software2efs.py  --cfg=/data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562768838/cfgs/pipeline.cfg 
 
 ASSUMPTIONS: 
       1) Both json template(template.json) and the pipeline.cfg have been generated under the same directory(cfgs)
       2) AWS CLI is installed on server running this script 
       3) The pipeline steps and standards followed as specified in our documentation
       4) Our file server bc-node02.mdibl.net is the designated server to run data migrations

The program will fail with error if anyone of the project's expected structures is missing or is invalid.

   '''
    print("%s"%(usage))

if __name__== "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "cfg="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print("ERROR:%s" % (str(err) )) # will print something like "option -a not recognized"
        prog_usage()
        sys.exit(1)
    #set program arguments
    pipeline_config=None
    log_file=None
    for o, a in opts:
        if o in ("-c", "--cfg"):pipeline_config = a
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
    datasync_obj=AwsDataSyncDOM()
    if biocore_obj.project_cwl_script is None or not isfile(biocore_obj.project_cwl_script):
        print("ERROR: Experiment cwl script file missing - see path:%s"%(biocore_obj.project_cwl_script))
        sys.exit()
    if biocore_obj.json_template is None or not isfile(biocore_obj.json_template):
        print("ERROR: Experiment json template file(template.json) missing - see path:%s"%(biocore_obj.json_template))
        sys.exit()
    if not isdir(biocore_obj.biocore_log_base):
        print("ERROR: Log directory missing - see:%s"%(biocore_obj.biocore_log_base ))
        sys.exit()
    
    log_file=join(biocore_obj.biocore_log_base,basename(__file__)+".log")
    log=open(log_file,'w') 
    log.write("**********************************\n")
    log.write("Starting Software Migration to AWS EFS \n")
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
    try:
        # get datasync  nfs and efs locations 
        datasync_locations=datasync_obj.get_locations()
        ## Create tasks for specified datasync locations as needed
        software_tasks=datasync_obj.create_software_tasks(biocore_obj.biocore_software_base,datasync_locations)
        ##get tasks status
        current_tasks=datasync_obj.get_tasks()
        for task_name,task in software_tasks.items():
            log.write("----------------------------\n")
            log.write("Transfer started:%s\n"%( datetime.now()))
            task_arn=task["TaskARN"]
            for label,value in task.items():
                log.write("%s:%s\n"%( label,value))
            if task_name in current_tasks:
                task_status=current_tasks[task_name]["status"]
                if "AVAILABLE" in task_status:
                    status=datasync_obj.start_task_execution(task_arn)
                    log.write("Task status:%s\n"%(status))
                else:
                    log.write("Task status:%s\n"%(task_status))
            else:log.write("Task status: error - Not found \n")
    except:raise
    log.write("Program complete\n")
    print("Program complete.\nCheck the logs:\n%s\n"%(log_file))
    sys.exit()
