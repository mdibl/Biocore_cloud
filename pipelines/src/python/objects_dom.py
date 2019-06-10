# -*- coding: utf-8 -*-
"""
Template data models for different dataset metadata.

Returns:
     Sets global  
Raises:
     Nothing
AwsDataSyncDOM: Stores AWS datasync connection object
BiocoreInfoDOM: Stores biocore info directories map
RnaSeqPipelineJsonDOM: Stores the data model of pipeline json file for rna-seq type analysis 
PipelinePcfDOM: Stores the data model of pipeline pcf file

Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: May 2019

"""
import subprocess as sp
import json

class AwsDataSyncDOM:
    def __init__(self):
        self.region_id="us-east-1"
        self.account_id="012870262837"
        self.subnet_id="subnet-6b46b90c"
        self.subnet_arn="arn:aws:ec2:us-east-1:012870262837:subnet/subnet-6b46b90c"
        self.security_group_id="sg-30f3ff79"
        self.security_group_arn="arn:aws:ec2:us-east-1:012870262837:security-group/sg-30f3ff79"
        self.onprem_agent_id="agent-09909c9a6255bde37"
        self.onprem_agent_arn="arn:aws:datasync:us-east-1:012870262837:agent/agent-09909c9a6255bde37"
        self.item_class={}
        #
        ##These are aws service class of interest to us
        self.item_class["efs"]="elasticfilesystem"
        self.item_class["s3"]="s3"
        self.item_class["datasync"]="datasync"
        self.item_class["subnet"]="ec2"
        self.item_class["security-group"]="ec2"
        #arn:aws:s3:::biocore-data
       
    ##
    #The unique Amazon Resource Names (ARNs) associated with this item
    #Example - arn:aws:datasync:us-east-1:012870262837:agent/agent-09909c9a6255bde37
    # item_class:
    #   1) efs file system: item_class=elasticfilesystem
    #   2) datasync: item_class=datasync
    #   3) subnet,security-group: item_class=ec2
    # item_name: [agent |location | task| subnet | security-group 
    def get_arn(self,item_class,item_name,item_id):
        arn="arn:aws:"+item_class+":"+self.region_id+":"+self.account_id+":"+item_name+"/"+item_id
        return arn
    #
    def get_ec2_config(self):
        return "SubnetArn="+self.subnet_arn+",SecurityGroupArns="+self.security_group_arn   
    ##
    # Get the agent status [ OFFLINE | ONLINE ]
    def get_agents_online(self):
        agents={}
        try:
            agents_list={}
            agents_lt=sp.Popen("aws datasync list-agents",shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
            agents_list=json.loads(agents_lt)
            if "Agents" in agents_list:
                for agent in agents_list["Agents"]:
                    agent_arn=agent["AgentArn"]
                    if "ONLINE" == agent["Status"]:
                        agents[agent_arn]=agent["Name"]
        except:raise
        return agents
    ##
    # get list of current efs file systems
    def get_efs_file_systems(self):
        file_systems={}
        try:
            f_systems_list=sp.Popen("aws efs describe-file-systems" ,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
            f_systems= json.loads(f_systems_list)
            if "FileSystems" in f_systems:
                for f_system in f_systems["FileSystems"]:
                    f_system_id=f_system["FileSystemId"]
                    file_systems[f_system_id]={}
                    file_systems[f_system_id]["Tags"]=f_system["Tags"]
                    file_systems[f_system_id]["LifeCycleState"]=f_system["LifeCycleState"]
                    file_systems[f_system_id]["NumberOfMountTargets"]=f_system["NumberOfMountTargets"]
        except:raise
        return file_systems
    
    ##
    # Get current locations. Store them by file system types
    # nfs, s3, efs
    def get_locations(self):
        locations={}
        try:
            locations_list=sp.Popen("aws datasync list-locations",shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
            loc_list=json.loads(locations_list)
            if "Locations" in loc_list:
                for location in loc_list["Locations"]:
                    if "s3:/" in location["LocationUri"]:
                        if "s3" not in locations: locations["s3"]=[]
                        locations["s3"].append(self.get_location("describe-location-s3",location["LocationArn"]))
                    if "nfs:/" in location["LocationUri"]:
                        if "nfs" not in locations: locations["nfs"]=[]
                        locations["nfs"].append(self.get_location("describe-location-nfs",location["LocationArn"]))
                    if "efs:/" in location["LocationUri"]:
                        if "efs" not in locations: locations["efs"]=[]
                        locations["efs"].append(self.get_location("describe-location-efs",location["LocationArn"]))
        except:pass
        return locations
    ##
    # Get the metadata for the specified location
    ## location_type=[describe-location-s3 | describe-location-nfs | describe-location-efs
    """
    """
    def get_location(self,location_type,location_arn):
        cmd="aws datasync "+location_type+" --location-arn "+location_arn
        return json.loads(sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
   
    def delete_location(self,location_arn):
        return sp.Popen("aws datasync delete-location --location-arn "+location_arn,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
    ##
    # Create location
    #def create_efs_location(self,subdirectory):
    #def create_nfs_location(self,):
    #def create_s3_location(self,):
    ##
    # get the metadata associated to 
    ## return the following object:
    """
    """
    def get_task(self,task_arn):
         return json.loads(sp.Popen("aws datasync describe-task --task-arn "+task_arn,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
    ##
    # get current tasks - task.TaskArn, task.Status, task.Name
    def get_tasks(self):
        tasks=[]
        try:
            tasks_list=json.loads(sp.Popen("aws datasync list-tasks",shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
            if "Tasks" in tasks_list:
                for task in tasks_list["Tasks"]:tasks.append(self.get_task(task["TaskArn"]))
        except:pass
        return tasks

class BiocoreInfoDOM:
    def __init__(self):
        self.external_data=None    #Where we store downloaded data
        self.internal_data=None    #Where we store internal data
        self.external_software=None    #Where we store downloaded packages
        self.internal_software=None    #Where we store internal packages
        self.scratch=None          #Working space
        self.transformed=None      #Where we store tools' generated indexes
        self.projects=None    #Completed projects space

    def set_external_data(self,ext_data_dir):
        self.external_data=ext_data_dir
    def set_internal_data(self,int_data_dir):
        self.internal_data=int_data_dir
    def set_external_software(self,ext_soft_dir):
        self.external_software=ext_soft_dir
    def set_internal_software(self,int_soft_dir):
        self.internal_software=int_soft_dir
    def set_scratch(self,scratch_dir):
        self.scratch=scratch_dir
    def set_transformed(self,transformed_dir):
        self.transformed=transformed_dir 
    def set_projects(self,projects_dir):
        self.projects=projects_dir

#class ExperimentConfigDOM:
"""
PipelinePcfDOM: A data model for the pipeline pcf file
    Members:
        1) CWL_SCRIPT: Full path to the cwl file 
        2) JSON_FILE: Full path to the pipeline json file 
        3) CWL_COMMAND_OPTIONS:Cwl Command line options
        4) PIPELINE_OWNER: The owner of the pipeline results directory 
        5) RESULTS_DIR: Full path to Pipeline results directory 
"""
class PipelinePcfDOM:
    def __init__(self,user_name,cwl_cmd_options,pipeline_results_base,json_file,cwl_script):
        self.cwl_script=None          #cwl script for this pipeline
        self.json_file=None           #json file for this pipeline
        self.cwl_cmd_options=None     #cwl command line options
        self.pipeline_owner=None         #User
        self.pipeline_results_base=None  #Where to store the pipeline results
        self.set_pipeline(user_name,cwl_cmd_options,json_file,cwl_script)

    def set_pipeline(self,user_name,cwl_cmd_options,pipeline_results_base,json_file,cwl_script)
        self.cwl_script=cwl_script
        self.json_file=json_file
        self.cwl_cmd_options=cwl_cmd_options
        self.pipeline_owner=user_name
        self.pipeline_results_base=pipeline_results_base

    def serialize(self):
        pcf_obj={}        
        pcf_obj["CWL_SCRIPT"]={}        
        pcf_obj["CWL_SCRIPT"]["label"]="Full path to the cwl file"        
        pcf_obj["CWL_SCRIPT"]["path"]=self.cwl_script
        pcf_obj["JSON_FILE"]={}       
        pcf_obj["JSON_FILE"]["label"]="Full path to the pipeline json file"  
        pcf_obj["JSON_FILE"]["path"]=self.json_file
        pcf_obj["CWL_COMMAND_OPTIONS"]={}
        pcf_obj["CWL_COMMAND_OPTIONS"]["label"]="Cwl Command line options"
        pcf_obj["CWL_COMMAND_OPTIONS"]["path"]=self.cwl_cmd_options
        pcf_obj["PIPELINE_OWNER"]={}
        pcf_obj["PIPELINE_OWNER"]["label"]="The owner of the pipeline results directory "
        pcf_obj["PIPELINE_OWNER"]["path"]=self.pipeline_owner
        pcf_obj["RESULTS_DIR"]={}
        pcf_obj["RESULTS_DIR"]["label"]="Pipeline results directory"
        pcf_obj["RESULTS_DIR"]["path"]=self.pipeline_results_base
        return pcf_obj

