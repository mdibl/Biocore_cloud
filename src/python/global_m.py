# -*- coding: utf-8 -*-

import subprocess as sp
from os import makedirs
import io, json

'''
Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: August 2019

'''

## Get global environment variables
## setting  from this project runID main config file 
def loadEnv(config_file):
    project_env={}
    output=sp.Popen("source "+config_file+";env",shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
    for line in output.splitlines():
        # Skip lines with comments
        if line.startswith("#"):continue 
        if "=" in line:
            try:
                key,value=line.split("=")
                project_env[key]=value
            except:pass
    return project_env

def mkdir_p(path):
    try:
        if not isdir(str(path)): makedirs(path)
    except:pass

## Creates a formatted json file given an object
def create_json_file(json_file,json_data):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str
    with io.open(json_file, 'w', encoding='utf8') as outfile:
         str_ = json.dumps(json_data,indent=4, sort_keys=True,separators=(',', ': '), ensure_ascii=False)
         outfile.write(to_unicode(str_))
                                        
