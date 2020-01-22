# code format: UTF-8
import subprocess as sp
from os.path import join,isfile,isdir,dirname,basename
import getopt,os,sys,re

# import io, json
from datetime import date,datetime

from biocore_project_dom import BiocoreProjectInfoDOM
import global_m as gb_m
from aws_datasync_dom import AwsDataSyncDOM

'''
Organization: MDIBL
Author(s): Lucie Hutchins, Nathaniel Maki
Contact: nmaki@mdibl.org
Date: January 2020

'''

def get_header():
    header = '''
****************** AWS S3 Data Migrations ***********************************************

The tool runs project-specific data migration from AWS S3 buckets to biocore file system.

*****************************************************************************************
    '''
    return header

def prog_use():
    usage = get_header()

    usage += '''

    Usage: 
        PROG [-h] -c path2/teamName/projectName/runID/cfgs/pipeline.cfg
        OR
        PROG [-h] --cfg=path2/teamName/projectName/runID/cfgs/pipeline.cfg

    Where:
        -h to show program usage
        -c path2runID/cfgs/pipeline.cfg or --cfg=path2runID/cfgs/pipeline.cfg ... required,
    
    Purpose: Utilizes pipeline.cfg and json template described in pipeline.cfg
             to migrate resultant experimental project and sample-specific data 
             back to local storage from the Amazon S3 file system

    Example:
        python mig_local2s3.py  -c /data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562768838/cfgs/pipeline.cfg
        OR
        python mig_local2s3.py  --cfg=/data/scratch/rna-seq/JimCoffman/jcoffman_001.embryo_cortisol_2015/jcoffman_001.1562768838/cfgs/pipeline.cfg
    
    Assumptions:
        1) User has full permissions on AWS S3 file system, as well as access to local system storage
        2) Both json template and pipeline.cfg have been generated under the same directory (cfgs)
        3) AWS CLI is installed on the server running this script
        4) Adherence to MDIBL pipeline steps and standards as specified in documentation
        5) File server bc-node02 is designated server to handle data migrations
    
    *** if projects expected structure(s) breaks any of the above conventions, program will error out ***

    '''
    print("%s"%(usage))