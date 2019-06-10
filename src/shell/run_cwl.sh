#!/bin/sh

#
#
# This job triggers a given pipeline analysis as specified in the input cwl file and json file. 
# Users can also specify cwltool options to use

CWLTOOL=`which cwltool`

CURRENT_USER=`id -un`
HOME=~
source /etc/profile.d/biocore.sh 

echo "`which fastqc`"
echo $PATH
date
script_name=`basename $0`

if [ ! -f ${CWLTOOL} ]
then
  echo "ERROR: cwltool not installed on `uname -n ` - see ${CWLTOOL}" 
  exit 1
fi
if [ -z "$RESULTS_DIR" ]
then
   echo ""
   echo "****************************************************"
   echo "*      Running Pipeline's cwl script               *"
   echo "****************************************************"
   echo ""
   echo "This job triggers the pipeline analysis as specified in the input cwl and json files."
   echo "Users can also specify cwltool options to use. "
   echo ""
   echo "Usage: ./$script_name CWL_SCRIPT JSON_FILE RESULTS_DIR CWL_COMMAND_OPTIONS"
   echo ""
   echo "Where:"
   echo "    CWL_SCRIPT: required - full path to the cwl script to use for this pipeline"
   echo "    JSON_FILE:  required - json file to use for this sample  - according to our standards"
   echo "    RESULTS_BASE: required - results base - according to our standards"
   echo "    CWL_COMMAND_OPTIONS:  optional(default: \"--no-container --debug  --timestamps\")"
   echo ""
   echo "Notes: The CWL_COMMAND_OPTIONS field if specified must be enclosed within \"\" double quotes."
   echo ""
   echo "Example:"
   echo "./$script_name path2/pipeline-pe-unstranded-with-sjdb.cwl path2/SL94881.danio_rerio.json path2/jcoffman_001.embryo_cortisol_2015/jcoffman_001_1559678964 \"--no-container --debug  --timestamps\""
   echo ""
   exit 1
fi
##############
#
#Tokens used to check the run status
ERROR_TERMS="ERROR error failed"
###############

if [[ -z "${CWL_SCRIPT}" ]] || [[ ! -f ${CWL_SCRIPT} ]]
then
  echo "ERROR: CWL_SCRIPT field is invalid" 
  exit 1
fi
if [[ -z "${JSON_FILE}" ]] || [[ ! -f ${JSON_FILE} ]]
then
  echo "ERROR: JSON_FILE field is invalid " 
  exit 1
fi
if [[ -z "${RESULTS_DIR}" || ! -d ${RESULTS_DIR} ]]
then
  echo "ERROR: pipeline results field is invalid - see: ${RESULTS_DIR} " 
  exit 1
fi
#
#set path to sample-specific results 
results_dir=$RESULTS_DIR/$sample_name
[ -d $RESULTS_DIR/logs ] && mkdir $RESULTS_DIR/logs
##############
log=$RESULTS_DIR/logs/$script_name.$sample_name.log
rm -f $log
touch $log

## Checks logs for failure 
function getLogStatus() {
  log=$1
  IFS=""
  rstatus="Success"
  for ((i = 0; i < ${#ERROR_TERMS[@]}; i++))
  do
       error_term=${ERROR_TERMS[$i]}
       error_found=`grep -i $error_term $log `
       if [ "$error_found" != "" ]
       then
            rstatus="Failure"
            echo "Found: \"$error_found\" "   
        fi
  done
  echo "$rstatus" 
}
echo "********************************************************" | tee -a $log
echo "Running : Sample - $sample_name  " | tee -a $log
echo "********************************************************"| tee -a $log

###############
#
if [ -d $results_dir ]
then
   if [ "$(ls -A $results_dir)" ]
   then
       echo "SKIPPING: Pipeline results directory not empty - check $results_dir" | tee -a $log
       exit 0
   fi
fi
#
[ ! -d $results_dir ] && mkdir -p $results_dir
if [ ! -d $results_dir ]
then
   echo "ERROR: Failed to create $results_dir" | tee -a $log
   exit 1
fi
## Set permissions on newly created directory
chown $CURRENT_USER $results_dir
chmod 775 $results_dir
## Run the command under $results_dir
TOP=`pwd`

cd $results_dir
echo "" 
echo "Running Command: $CWLTOOL $CWL_COMMAND_OPTIONS ${CWL_SCRIPT} ${JSON_FILE}" | tee -a $log
echo ""

$CWLTOOL $CWL_COMMAND_OPTIONS ${CWL_SCRIPT} ${JSON_FILE} 2>&1 | tee -a $log

#
echo " " | tee -a ${log}
echo "******************************************************" | tee -a ${log}
echo "Run sanity check" | tee -a ${log}
run_status=`getLogStatus ${log}`
echo "${run_status}" | tee -a $log
[ "${run_status}" != Success ] && exit 1
#
echo "" | tee -a ${log}
echo "Program complete - Check results under $results_dir"| tee -a ${log}   
date
echo "****************************************************" | tee -a ${log}

exit 0
