# -*- coding: utf-8 -*-
"""
Template data models for biocore info organization.

Returns:
     Sets global  
Raises:
     Nothing

BiocoreProjectInfoDOM: Maps biocore project's specific data files  
and directories. Uses the project main config and the json template
to generate the project's list of data and software to migrate to the cloud. 

Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: May 2019
Modified: July 2019

"""
import subprocess as sp
from os.path import isdir,join,isfile,basename,dirname
import json
from os import listdir
import  global_m as gb_m

class BiocoreProjectInfoDOM:
    def __init__(self,project_config):
        self.biocore_s3_data_base="/s3-drives/biocore-data"
        self.biocore_s3_data_uri="s3://biocore-data"
        self.biocore_data_base="/data"
        self.biocore_software_base="/opt/software" #base directory for software packages

        self.project_cwl_script=None         #Path to the project cwl script file
        self.project_design_file=None        #Path to the project design file
        self.project_run_id=None              #this project runID
        self.project_team_id=None            #this project team name
        self.project_name=None               #this project name
        self.bicore_pipelinemeta_dir=None    #where the pipeline pcf files are read/stored
        self.bicore_pipelinejson_dir=None    #where the pipeline json files are read/stored
        self.biocoree_reads_base=None        #where the sequence read files are stored
        self.biocore_index_base=None         #base directory for tool indexes
        self.biocore_log_base=None           #base directory for generated logs - stored by program
        ##Use json template to get
        ## 1) list of items of class File
        ## 2) list of items of class Directory
        self.json_template_files=[]
        self.json_template_directories=[]
        self.json_template=None

        ##maps bicore path to S3 path
        self.s3_biocore_items_map={}
        ##maps bicore path to efs path
        self.efs_biocore_items_map={}
        
        ##load containers
        self.set_project(project_config)
        self.set_biocore_cloud_items_list()

    def set_project(self,project_config):
        project_env=gb_m.loadEnv(project_config)
        if project_env["DESIGN_FILE"]: self.project_design_file=project_env["DESIGN_FILE"]
        if project_env["PROJECT_TEAM_NAME"]: self.project_team_id=project_env["PROJECT_TEAM_NAME"]
        if project_env["PROJECT_NAME"]: self.project_name=project_env["PROJECT_NAME"]
        if project_env["LOG_BASE"]: self.biocore_log_base=project_env["LOG_BASE"]
        if project_env["CWL_SCRIPT"]: self.project_cwl_script=project_env["CWL_SCRIPT"]
        if project_env["RUN_ID"]: self.project_run_id=project_env["RUN_ID"]
        if project_env["READS_BASE"]:self.biocoree_reads_base=project_env["READS_BASE"]
        if project_env["PATH2_JSON_FILES"]:self.bicore_pipelinejson_dir=project_env["PATH2_JSON_FILES"]
        if project_env["PIPELINE_META_BASE"]:self.bicore_pipelinemeta_dir=project_env["PIPELINE_META_BASE"]
        if project_env["JSON_TEMPLATE"]:
            self.json_template=project_env["JSON_TEMPLATE"]
            try:
                with open(project_env["JSON_TEMPLATE"]) as f:
                    json_temp_obj=json.load(f)
                for key in list(json_temp_obj.keys()):
                    data=json_temp_obj[key]
                    if isinstance(data,list):
                        for index,item in enumerate(data):
                            if isinstance(item,dict):
                                if "File" in item["class"]:
                                    if isfile(str(item["path"])):self.json_template_files.append(item["path"])
                                elif "Directory" in item["class"]:
                                    if isdir(str(item["location"])):self.json_template_directories.append(item["location"])
                    elif isinstance(data,dict):
                        if "File" in data["class"]:
                            if isfile(str(data["path"])):self.json_template_files.append(data["path"])
                        elif "Directory" in data["class"]:
                            if isdir(str(data["location"])):self.json_template_directories.append(data["location"])
                    else:
                        if isfile(str(data)):self.json_template_files.append(data)
            except:pass       
        
    ##Create expected directory structure for pipelines pcf base directory
    ##
    def get_s3_path(self,biocore_path):
        return biocore_path.replace(self.biocore_data_base,self.biocore_s3_data_base)

    def create_s3_dir(self,s3_dir):makedir_p(s3_dir)

    def get_samples(self):
        samples=[]
        try:
            if isfile(str(self.project_design_file)):
                with open(str(self.project_design_file)) as f:
                    for line in f.readlines():
                        if "Sample" in line or "sample" in line: continue
                        fields=line.split("\t")
                        samples.append(fields[0].strip())
        except:raise
        return samples

    def get_reads(self):
        reads_base_files=[f for f in listdir(self.biocoree_reads_base) if isfile(join(self.biocoree_reads_base,f))]
        reads=[]
        for sample_id in self.get_samples(): 
            for file_name in [f for f in listdir(self.biocoree_reads_base) if isfile(join(self.biocoree_reads_base,f))]:
                if file_name.startswith(sample_id):
                    reads.append(join(self.biocoree_reads_base,file_name))
        return reads
     

    def set_biocore_cloud_items_list(self):
        self.s3_biocore_items_map={}
        self.efs_biocore_items_map={}
        self.efs_biocore_items_map[self.project_cwl_script]=self.project_cwl_script
        self.s3_biocore_items_map[self.bicore_pipelinemeta_dir]=self.get_s3_path(self.bicore_pipelinemeta_dir)
        self.s3_biocore_items_map[self.bicore_pipelinejson_dir]=self.get_s3_path(self.bicore_pipelinejson_dir)
        for read_file in self.get_reads():
            self.s3_biocore_items_map[read_file]=self.get_s3_path(read_file) 
        ##get additional data transfer candidates from json template used
        for item_name in self.json_template_files+self.json_template_directories:
            cloud_path=self.get_s3_path(item_name)
            if self.biocore_s3_data_base in cloud_path:self.s3_biocore_items_map[item_name]=cloud_path
            elif self.biocore_software_base in item_name:self.efs_biocore_items_map[item_name]=item_name
            

if __name__== "__main__":
    msg="Hello"
    config_file="/data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562611492/cfgs/pipeline.cfg"
    print("%s\n"%(msg))
    biocore_obj=BiocoreProjectInfoDOM(config_file)
    print("\n********************\nList of items to migrate to  S3 bucket:\n********************\n")
    for biocore_path,s3_path in biocore_obj.s3_biocore_items_map.items():
        print("Path on biocore servers:%s\nPath on AWS S3 :%s\n____________________"%(biocore_path,s3_path))
    print("\n********************\nList of items to migrate to AWS EFS file system:\n********************\n")
    for biocore_path,efs_path in biocore_obj.efs_biocore_items_map.items():
         print("Path on biocore servers:%s\nPath on AWS EC2 instance:%s\n____________________"%(biocore_path,efs_path)) 
    
    
