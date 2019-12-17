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
        self.project_reads_base=None         #where the original sequence read files are stored
        self.scratch_reads_base=None         #where the sequence read files are stored on scracth
        self.project_results_base=None       #where the pipeline results are stored on scracth
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

    ## get list of samples
    def get_exp_samples(self):
        samples=[]
        design_file=self.project_design_file
        with open(design_file,'r') as f:
            try:
                for line in f.readlines():
                    if "Sample" in line:continue
                    if "sample_id" in line:continue
                    #Remove leading and trailing whitespace from line
                    line=line.strip()
                    fields=line.split('\t')
                    ##sample_id is the first field of the array
                    samples.append(fields[0].strip())
            except:pass
        return samples

    #### get list of reads file names
    def get_reads_list(self,read_suffix):
        reads_base=self.project_reads_base
        reads_list={}
        try:
            reads=[f for f in listdir(reads_base) if isfile(join(reads_base,f))]
            samples=self.get_exp_samples()
            for read in reads:
                read_file_name=read.strip() 
                if read_file_name.endswith(read_suffix):
                    for sample in samples:
                        if read_file_name.startswith(sample):
                            if sample not in reads_list: reads_list[sample]=[]
                            reads_list[sample].append(read_file_name)
        except:pass
        return reads_list

    def set_project(self,project_config):
        project_env=gb_m.loadEnv(project_config)
        if project_env["DESIGN_FILE"]: 
            self.project_design_file=project_env["DESIGN_FILE"]
            self.project_reads_base=dirname(project_env["DESIGN_FILE"])
        if "ORIGINAL_READS_BASE" in project_env:
            self.project_reads_base=project_env["ORIGINAL_READS_BASE"]
        if project_env["PROJECT_TEAM_NAME"]: self.project_team_id=project_env["PROJECT_TEAM_NAME"]
        if project_env["PROJECT_NAME"]: self.project_name=project_env["PROJECT_NAME"]
        if project_env["LOG_BASE"]: self.biocore_log_base=project_env["LOG_BASE"]
        if project_env["CWL_SCRIPT"]: self.project_cwl_script=project_env["CWL_SCRIPT"]
        if project_env["RUN_ID"]: self.project_run_id=project_env["RUN_ID"]
        if project_env["READS_BASE"]:self.scratch_reads_base=project_env["READS_BASE"]
        if project_env["RESULTS_DIR"]:self.project_results_base=project_env["RESULTS_DIR"]
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
    ##
    # returns the URI of our S3 path
    def get_s3_uri(self,s3_path):
        return s3_path.replace(self.biocore_s3_data_base, self.biocore_s3_data_uri)

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
        reads_base_files=[f for f in listdir(self.scratch_reads_base) if isfile(join(self.scratch_reads_base,f))]
        reads=[]
        for sample_id in self.get_samples(): 
            for file_name in [f for f in listdir(self.scratch_reads_base) if isfile(join(self.scratch_reads_base,f))]:
                if file_name.startswith(sample_id):
                    reads.append(join(self.scratch_reads_base,file_name))
        return reads
     

    def set_biocore_cloud_items_list(self):
        self.s3_biocore_items_map={}
        self.efs_biocore_items_map={}
        self.efs_biocore_items_map[self.project_cwl_script]=self.project_cwl_script
        self.s3_biocore_items_map[self.bicore_pipelinemeta_dir]=self.get_s3_path(self.bicore_pipelinemeta_dir)
        self.s3_biocore_items_map[self.bicore_pipelinejson_dir]=self.get_s3_path(self.bicore_pipelinejson_dir)
        self.s3_biocore_items_map[self.project_reads_base]=self.get_s3_path(self.scratch_reads_base)
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
    s3_path=biocore_obj.get_s3_path(biocore_obj.project_results_base)
    print("Project RunID base:\nBiocore path:%s\nCloud path:%s\n"%(biocore_obj.project_results_base,s3_path))
    read_suffix="fastq.gz"
    samples=biocore_obj.get_reads_list(read_suffix)
    for sample,reads in samples.items():
        print("%s: %s"%(sample,";".join(reads)))
    
    
