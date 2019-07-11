# -*- coding: utf-8 -*-

import subprocess as sp
from os import makedirs
import io, json

## Get global environment variables
## setting  from this project runID main config file 
def loadEnv(config_file):
    project_env={}
    output=sp.Popen("source "+config_file+";env",
                     shell=True, stdout=sp.PIPE, stderr=sp.STDOUT).stdout.read()
    for line in output.splitlines():
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

def create_json_file(json_file,json_data):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str
    with io.open(json_file, 'w', encoding='utf8') as outfile:
         str_ = json.dumps(json_data,indent=4, sort_keys=True,separators=(',', ': '), ensure_ascii=False)
         outfile.write(to_unicode(str_))
                                        
