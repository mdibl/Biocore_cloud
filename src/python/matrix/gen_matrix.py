# -*- coding: utf-8 -*-
import getopt,os,sys
from  datetime import datetime
from os import makedirs,chdir,getcwd
from os.path import isdir,dirname,abspath,basename
import memory_profiler as mem_profile
import random
import time
from glob import glob
from matrix import MatrixDOM

'''
Organization: MDIBL
Author: Lucie N. Hutchins
Contact: lucie.hutchins@mdibl.org
Date: January 2019
'''
def get_header():
    header='''
****************** gen_matrix ********************************************************

The tool generates a matrix file under the specified --outdir  .

***************************************************************************************
    '''
    return header

def prog_usage():
    usage='''
****************** gen_matrix ********************************************************

The tool generates a matrix file under the specified destdir  .

***************************************************************************************

 Usage: PROG [-h] --infiles="files" --outdir=path2/output_prefix --jindex=indexOfColumnValues 
        [--prefix=results_prefix] [--vindex=indexOfRowIDs] [--round] [--mvalue=missing_value]

 Where:
     -h To show the usage
     -i path2/files Or --infiles=path2/files  ... required, 
        specifies a commas-separated(or a wildcard)list of input files (takes wildcard)
     -o path2/output_dir Or  --outdir=path2/output_dir ... required, 
        default results dir is working directory
     -j indexOfColumnValues or --jindex=indexOfColumnValues ... required, 
        specifies the column index of the values 
     -p result_prefix  Or --prefix=results_prefix  ... optional default gen_matrix
        specifies the the name of the results file
     -v indexOfRowIDs or --vindex=indexOfRowIDs ... optional default first column(index=0)  
     --round or -r   
     --mvalue=missing_value   or -m missing_value  ... optional missing value (default "")   
      
 Notes: You MUST enclose the input files argument within the "" since it could 
        contain wildcard or space between files.

 Output: Generate a matrix file and associated log under the path specified by --outdir 
         where the format of the results file is output_prefix.vindex_column_name.jindex_column_name.* 

 Example: 
       python PROG  -i "input_path2/project1/*.genes.resutls" -o out_path2/project1/genes --prefix=genes_matrix -j 4 -m 0 
       OR 
       python PROG --infiles="input_path2/project1/*.genes.results" --outdir=out_path2/project1/genes -p genes_matrix --jindex=4
       OR
       python PROG  -i "input_patH2/f1.genes.resutls,input_patH2/f1.genes.resutls" -o out_path2/project1/genes -p genes_matrix -j 4 
           
 ASSUMPTIONS: 
       1) User has full permission to create the results directory specified in --outdir
       2) Note that the input files argument MUST be enclosed within the quote ""
   '''
    print("%s"%(usage))

if __name__== "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:o:p:j:v:m:r", 
                    ["help", "infiles=","outdir=","prefix=","jindex=","vindex=","mvalue=","round"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print("ERROR:%s" % (str(err) )) # will print something like "option -a not recognized"
        prog_usage()
        sys.exit(1)
    #set program arguments
    input_files=None
    output_dir=None
    output_prefix=None
    jindex=None
    vindex=0
    missing_value=""
    round_res=False
    for o, a in opts:
        if o in ("-i", "--infiles"):input_files = a
        elif o in ("-o", "--outdir"):output_dir = a
        elif o in ("-p", "--prefix"):output_prefix = a
        elif o in ("-j","--jindex"):jindex = int(a)
        elif o in ("-v","--vindex"):vindex = int(a) 
        elif o in ("-r","--round"):round_res = True
        elif o in ("-m","--mvalue"):missing_value = a
        elif o in ("-h", "--help"):
            prog_usage()
            sys.exit()
        else:
            assert False, "unhandled option"
    if input_files is None:
        print("ERROR: Input files not specified") # will print something like "option -a not recognized"
        prog_usage()
        sys.exit()
    if jindex is None:
        print("ERROR: Target column index must be specified")
        prog_usage()
        sys.exit()
    ##Get working directory
    if output_prefix is None:output_prefix="gen_matrix"
    if output_dir is None:
       output_dir=dirname(__file__)
    ## Create output directory as needed
    destdir_base=abspath(output_dir)
    if not isdir(destdir_base):
        makedirs(destdir_base,mode=0o777)
    ## Get a list of input files
    input_files_list=[]
    if '*' in input_files:
        input_files_list=glob(input_files)
    else:
        input_files_list=input_files.split(',')
    header=get_header()
    t1= time.clock()
    mem_before=str(mem_profile.memory_usage())
    start_time=datetime.now()

    ## Create a matrix object
    obj=MatrixDOM(input_files_list,vindex,jindex,round_res)
    matrix_label=obj.get_matrix_label()
    rowLabel=matrix_label["rowLabel"]
    targetColumnLabel=matrix_label["targetLabel"]
    ## Create a log file
    res_prefix=destdir_base+"/"+output_prefix+"."+rowLabel+"."+targetColumnLabel
    log_file=res_prefix+".log"
    results_file=res_prefix+".txt"
    print("%s"%(header))
    print("The tool will generate the following two files:")
    print("Log File:  %s"%(log_file))
    print("Results File:  %s"%(results_file))

    print("") 
    with open(log_file,"w") as log:
        log.write("%s\n"%(header))
        log.write("Output Directory: %s\n"%(destdir_base))
        log.write("Results File: %s\n"%(results_file))
        log.write("Target Colunm index: %d\n"%(jindex))
        log.write("Colunm index of rowIDs: %d\n"%(vindex))
        log.write("Round results: %s\n"%(round_res))
        log.write("Input Files Count: %s\n"%(len(input_files_list)))
        log.write("Input Files List:\n")
        log.write("==\n")
        obj.gen_files_summary(log)
        with open(results_file,'w') as fd:
            obj.get_panda_matrix(fd,missing_value)
   
        log.write("==\n")
        log.write("Program Started: %s\n"%(start_time))
        log.write("Program Ended: %s\n"%(datetime.now()))
        log.write("Memory Usage Before: %s MB\n"%(mem_before))
        log.write("Memory Usage After: %s MB\n"%(str(mem_profile.memory_usage())))
        print("Program ended at:%s"%(datetime.now()))
        t2= time.clock()
        print("Matrix generator took %s seconds"%(str(t2-t1)))
        log.write("Matrix generator took %s seconds"%(str(t2-t1)))

    sys.exit()
