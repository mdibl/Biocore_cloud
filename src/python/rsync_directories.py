# -*- coding: utf-8 -*-
from os.path import isdir,basename,join
import getopt,sys
import global_m as gb
from datetime import date

'''
Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: August 2019

'''
def get_header():
    header='''
****************** rsync_directory **************************************************

This script uses the system rsync utils to synch the content of two directories - source_dir and dest_dir
    '''
    return header

def prog_usage():
    usage=get_header()
    usage+='''
 Usage: PROG [-h] -s source_dir -d dest_dir
 Where:
     -h To show the usage
     -s path2/source_dir  or --src=path2/source_dir  ... required, 
     -d path2/dest_dir or --dest=path2/dest_dir ... required
      
 Example: 
       python PROG  -s /data/projects/Biocore/biocore_analysis -d /home/bioadmin/git_repos/biocore_analysis
       OR
       python PROG  --src=/data/projects/Biocore/biocore_analysis -dest=/home/bioadmin/git_repos/biocore_analysis

 Where PROG is this script name - 

 The program assumes one of the following:
 1) source_dir and dest_dir are local to the server running this script
 2) OR in case one or both target directories are on a remote server, 
    the user has established passwordless connection between the local server running this program
    and the remote server hosting the target directories.   
   '''
    print("%s"%(usage))

##
if __name__== "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:d:",
                    ["help", "src=","dest="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print("ERROR:%s" % (str(err) )) # will print something like "option -a not recognized"
        prog_usage()
        sys.exit(1)
    #set program arguments
    source_dir=None
    dest_dir=None
    log_file=None
    for o, a in opts:
        if o in ("-s", "--src"):source_dir = a.strip()
        elif o in ("-d","--dest"):dest_dir = a.strip()
        elif o in ("-h", "--help"):
            prog_usage()
            sys.exit()
        else:
            assert False, "unhandled option"
    #validate the input
    if source_dir is None or dest_dir is None:
        prog_usage()
        sys.exit()
    if  not isdir(source_dir):
        print("ERROR: Bad source directory - see:%s "%(source_dir))
        prog_usage()
        sys.exit()
    if  not isdir(dest_dir):
        print("ERROR: Bad destination directory - see:%s "%(dest_dir))
        prog_usage()
        sys.exit()
    
    ##reformat the input
    if not source_dir.endswith("/"):source_dir+="/"
    if not dest_dir.endswith("/"):dest_dir+="/"
    target_dir=dest_dir
    if target_dir.endswith("/"):target_dir=target_dir[:-1]
    project_env=gb.loadEnv("~/.bashrc")
    log_file=basename(__file__)+".log"
    if isinstance(project_env, dict) and "LOGS_BASE" in project_env:
        if not isdir(project_env["LOGS_BASE"]):
            gb.mkdir_p(project_env["LOGS_BASE"])
        log_file=join(project_env["LOGS_BASE"],basename(target_dir)+"."+basename(__file__)+".log")
    ## rsync the content between the source and destination directories
    log=open(log_file,'w')
    log.write("**********************************\n")
    log.write("**********************************\n")
    log.write("Date:%s\n"%( date.today()))
    print("Date:%s\n"%( date.today()))
    log.write("\n")
    log.write("Log file:%s\n"%(log_file))
    log.write("Source:%s\nDestination:%s\n"%(source_dir,dest_dir))
    print("Source:%s\nDestination:%s\n"%(source_dir,dest_dir))
    logs=gb.rsync_directories(source_dir,dest_dir)
    log.write("\nRSYNC LOGS:%s\n"%(logs))
    print("Program complete")
    print("For rsync logs, check log file:%s\n"%(log_file))
    sys.exit()
