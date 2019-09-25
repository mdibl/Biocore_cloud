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
from os.path import isdir,join,isfile,basename
import json
import  global_m as gb_m

class AwsDataSyncDOM:
    def __init__(self,account_id,agent_id,agent_ip):
        self.region_id="us-east-1"
        self.account_id=account_id
        self.subnet_id="subnet-6b46b90c"
        self.subnet_arn="arn:aws:ec2:us-east-1:012870262837:subnet/subnet-6b46b90c"
        self.security_group_id="sg-30f3ff79"
        self.security_group_arn="arn:aws:ec2:us-east-1:012870262837:security-group/sg-30f3ff79"
        self.onprem_agent_id=agent_id
        self.onprem_agent_ip=agent_ip
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
    def get_locations(self,location_type=None):
        locations={}
        try:
            locations_list=sp.Popen("aws datasync list-locations",shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
            loc_list=json.loads(locations_list)
            if "Locations" in loc_list:
                for location in loc_list["Locations"]:
                    if "s3:/" in location["LocationUri"]:
                        if "s3" not in locations: locations["s3"]=[]
                        locations["s3"].append(self.get_location("describe-location-s3",location["LocationArn"]))
                    elif "nfs:/" in location["LocationUri"]:
                        if "nfs" not in locations: locations["nfs"]=[]
                        locations["nfs"].append(self.get_location("describe-location-nfs",location["LocationArn"]))
                    elif "efs:/" in location["LocationUri"]:
                        if "efs" not in locations: locations["efs"]=[]
                        locations["efs"].append(self.get_location("describe-location-efs",location["LocationArn"]))
        except:raise
        if  location_type is not None and location_type in locations:
            return locations[location_type]
        else:
            return locations

    def get_nfs2efs_locations(self,locations):
        loc_map={}
        if "nfs" in locations and "efs" in locations:
            efs_locs={}
            #load efs software locations endpoints by endpoint directory target 
            for efs_loc in locations["efs"]:
                efs_loc_arn=efs_loc["LocationArn"]
                efs_loc_uri=efs_loc["LocationUri"]
                target_dir=basename(efs_loc_uri)
                if efs_loc_uri.endswith("/"):
                    target_dir=basename(efs_loc_uri[:-1])
                if target_dir not in efs_locs:efs_locs[target_dir]={}
                efs_locs[target_dir]["arn"]=efs_loc_arn
                efs_locs[target_dir]["uri"]=efs_loc_uri
            for nfs_location in locations["nfs"]:
                nfs_loc_arn=nfs_location["LocationArn"] 
                nfs_loc_uri=nfs_location["LocationUri"] 
                target_dir=basename(nfs_loc_uri)
                if nfs_loc_uri.endswith("/"):
                    target_dir=basename(nfs_loc_uri[:-1])
                if target_dir not in loc_map:loc_map[target_dir]={}
                loc_map[target_dir]["nfs_arn"]=nfs_loc_arn
                loc_map[target_dir]["nfs_uri"]=nfs_loc_uri
                loc_map[target_dir]["efs_arn"]=None
                loc_map[target_dir]["efs_uri"]=None
                if target_dir in efs_locs:
                    loc_map[target_dir]["efs_arn"]=efs_locs[target_dir]["arn"]
                    loc_map[target_dir]["efs_uri"]=efs_locs[target_dir]["uri"]
        return loc_map
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

    def create_nfs_location(self,subdir,onprem_config):
        cmd="aws datasync create-location-nfs --subdirectory "+subdir+" --server-hostname "+self.onprem_agent_ip
        cmd+=" --on-prem-config "+onprem_config
        return sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
    #def create_s3_location(self,):
    ##
    # get the metadata associated to 
    ## return the following object:
    """
    """
    def get_task(self,task_arn):
        cmd="aws datasync describe-task --task-arn "+task_arn
        return json.loads(sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())

    #https://docs.aws.amazon.com/datasync/latest/userguide/monitor-task-execution.html
    def get_task_execution(self,task_execution_arn):
        cmd="aws datasync describe-task-execution --task-execution-arn "+task_execution_arn
        return json.loads(sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
    ##
    # get current tasks - task.TaskArn, task.Status, task.Name
    def get_tasks(self):
        tasks={}
        try:
            tasks_list=json.loads(sp.Popen("aws datasync list-tasks",shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
            if "Tasks" in tasks_list:
                for task in tasks_list["Tasks"]:
                    task_name=task["Name"]
                    tasks[task_name]={}
                    tasks[task_name]["arn"]=task["TaskArn"]
                    tasks[task_name]["status"]=task["Status"]
        except:raise
        return tasks

    
    def delete_task(self,task_arn):
        return sp.Popen("aws datasync delete-task --task-arn "+task_arn,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()

    # Create a datasync task - output the task arn
    def create_task(self,src_loc_arn,dest_loc_arn,task_name=None):
        datasync_cmd="aws datasync create-task --source-location-arn "+src_loc_arn+" --destination-location-arn "+dest_loc_arn
        if task_name is not None:datasync_cmd+=" --name "+task_name
        return sp.Popen(datasync_cmd ,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
    #
    ## create a task for each nfs-efs location pair  
    # 
    def create_software_tasks(self,biocore_software_base,datasync_locations):
        nfs2efs_location_map=self.get_nfs2efs_locations(datasync_locations)
        current_tasks=self.get_tasks()
        d_locations={}
        if isinstance(nfs2efs_location_map,dict):
            for target_dir,locations in nfs2efs_location_map.items():
                task_name="software-"+target_dir
                d_locations[task_name]={}
                d_locations[task_name]["Datasync "]=join(biocore_software_base,target_dir)
                d_locations[task_name]["Local NFS Source location"]=locations["nfs_uri"]
                d_locations[task_name]["NFS location ARN"]=locations["nfs_arn"]
                d_locations[task_name]["Amazon EFS Destination location"]=locations["efs_uri"]
                d_locations[task_name]["EFS location ARN"]=locations["efs_arn"]
                d_locations[task_name]["TaskName"]=task_name
                if task_name in current_tasks:task_arn=current_tasks[task_name]["arn"]
                else:
                    print("Creating task: %s"%(task_name))
                    task_arn=self.create_task(locations["nfs_arn"],locations["efs_arn"],task_name)
                d_locations[task_name]["TaskARN"]=task_arn
        return d_locations

    def start_task_execution(self,task_arn):
         cmd="aws datasync start-task-execution --task-arn "+task_arn
         return sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read() 

    #### S3 sync
    def s3_sync(self,source_dir,destination_dir,include_file=None):
        include_token=""
        if include_file is not None:include_token=" --include "+include_file
        cmd="aws s3 sync "+source_dir+" "+destination_dir+include_token
        return sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
    ### EFS file system
    def get_current_efs(self):
        cmd="aws efs describe-file-systems"
        efs_files={}
        try:
            efs_list=json.loads(sp.Popen(cmd,shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read())
            for index, efs in enumerate(efs_list):
                print("FileSystemId:%s\nLifeCycleState:%s\nTags:%s"%efs["FileSystemId"],efs["LifeCycleState"],efs["Tags"]())
        except:pass
        return efs_files
