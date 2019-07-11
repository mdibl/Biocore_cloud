# -*- coding: utf-8 -*-
"""
Template data models for different dataset metadata.

Returns:
     Sets global  
Raises:
     Nothing
AwsDataSyncDOM: Stores AWS datasync connection object

Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: May 2019
Modified: July 2019

"""
import subprocess as sp
from os.path import isdir,join,isfile
import json
import  global_m as gb_m

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
    def create_efs_location(self,subdir,filesystem_arn):
        cmd="aws datasync create-location-efs --subdirectory "+subdir+" --efs-filesystem-arn "+filesystem_arn
        cmd+=" --ec2-config "+self.get_ec2_config()
        return sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()

    #def create_nfs_location(self,):
    #def create_s3_location(self,):
    ##
    # get the metadata associated to 
    ## return the following object:
    """
    """
    def get_task(self,task_arn):
         cmd="aws datasync describe-task --task-arn "+task_arn
         return json.loads(sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
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

    def delete_task(self,task_arn):
        return sp.Popen("aws datasync delete-task --task-arn "+task_arn,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()

    def create_task(self,src_loc_arn,dest_loc_arn):
        datasync_cmd="aws datasync create-task --source-location-arn "+src_loc_arn+" --destination-location-arn "+dest_loc_arn
        return sp.Popen(datasync_cmd ,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()

    def start_task_execution(self,task_arn):
         cmd="aws datasync start-task-execution --task-arn "+task_arn
         return sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read() 

    #### S3 sync
    def s3_sync(self,source_dir,destination_dir,include_file=None):
        include_token=""
        if include_file is not None:include_token=" --include "+include_file
        cmd="aws s3 sync "+source_dir+" "+destination_dir+include_token
        return sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
