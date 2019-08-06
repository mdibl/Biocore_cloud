#!/bin/sh

#
#
# This job triggers a given sample pipeline analysis as specified in the input cwl file and json file. 
# Users can also specify cwltool options to use

CWLTOOL=`which cwltool`
CURRENT_USER=`id -un`
source /etc/profile.d/biocore.sh 

date
script_name=`basename $0`

if [ ! -f ${CWLTOOL} ]
then
  echo "ERROR: cwltool not installed on `uname -n ` - see ${CWLTOOL}" 
  exit 1
fi
CWL_SCRIPT=$1
JSON_FILE=$2
RESULTS_DIR=$3
CWL_COMMAND_OPTIONS="--no-container --debug  --timestamps"

[ ! -z "$4" ] && CWL_COMMAND_OPTIONS=$4

if [[ -z "${CWL_SCRIPT}" || -z "$JSON_FILE" || -z "$RESULTS_DIR" ]]
then
   echo ""
   echo "****************************************************"
   echo "*      Running Pipeline's cwl script"
   echo "****************************************************"
   echo ""
   echo "This job triggers the pipeline analysis for the specified sampleID."
   echo "Users can also specify cwltool options to use. "
   echo ""
   echo "Usage: ./$script_name path2_cwl_script path2_json_file path2_project_run_results [CWL_COMMAND_OPTIONS]"
   echo ""
   echo "Where:"
   echo "path2_cwl_script : Required - is the full path to this pipeline cwl script."
   echo "path2_json_file:   Required - is the full path to this pipeline json file."
   echo "path2_project_run_results:   Required - is the full path to where to strore the results."
   echo ""
   echo "CWL_COMMAND_OPTIONS:  optional(default: \"--no-container --debug  --timestamps\")"
   echo ""
   echo "Notes: The CWL_COMMAND_OPTIONS field if specified must be enclosed within \"\" double quotes."
   echo ""
   echo "Example:"
   echo "./$script_name /opt/software/external/.../pipeline-se-unstranded-with-sjdb.cwl \
         /data/project/.../vyin_010.1560549433/SL375032.danio_rerio.json \
        /data/scratch/../vyin_010.1560549433  \"--no-container --debug  --timestamps\""
   echo ""
   exit 1
fi
##############
#
#Tokens used to check the run status
ERROR_TERMS="ERROR error failed permanentFail"
###############
LOG_BASE=$RESULTS_DIR/logs
[ ! -d $LOG_BASE ] && mkdir -p $LOG_BASE
## 
json_filename=`basename ${JSON_FILE}`
sample_name=$(echo $json_filename  | cut -d'.' -f 1)
## Assumption run_id follows our naming standards: pixxx.timestamp
run_id=`basename $RESULTS_DIR`
timestamp_id=$(echo $run_id | cut -d'.' -f 2)

log=$LOG_BASE/$script_name.$sample_name.log
[ -f $log ] && rm -f $log
touch $log

echo ""|tee -a $log

if [ ! -f ${CWL_SCRIPT} ]
then
  echo "ERROR: cwl script missing - see: $CWL_SCRIPT " | tee -a $log
  exit 1
fi
if [ ! -f ${JSON_FILE} ]
then
  echo "ERROR: json file for this sample missing - see $JSON_FILE" | tee -a $log 
  exit 1
fi
if [ ! -d ${RESULTS_DIR} ]
then
  echo "ERROR: Project result directory missing - see: ${RESULTS_DIR} "  | tee -a $log
  exit 1
fi
echo ""|tee -a $log
echo "************************************************************************" | tee -a $log
echo "*      SampleID: $sample_name                   "| tee -a $log
echo "*      Date:  `date`                  "| tee -a $log
echo "*      Current User: `id -un`                  "| tee -a $log
echo "*      Results Base:  $RESULTS_DIR                "| tee -a $log
echo "*      Cwl Script:$CWL_SCRIPT                  "| tee -a $log
echo "*      Sample Json File:$JSON_FILE                  "| tee -a $log
#
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
#
#set path to sample-specific results 
sample_results_dir=$RESULTS_DIR/$sample_name
###############
#
if [ -d $sample_results_dir ]
then
   if [ "$(ls -A $sample_results_dir)" ]
   then
       echo "Archiving previous run results to $sample_results_dir.archive" | tee -a $log
       mv $sample_results_dir $sample_results_dir.archive
   fi
fi
#
[ ! -d $sample_results_dir ] && mkdir -p $sample_results_dir
## Set permissions on newly created directory
chmod g+w $sample_results_dir

## Run the command under $results_dir
cd $sample_results_dir
#Command Line
CMD="$CWLTOOL $CWL_COMMAND_OPTIONS ${CWL_SCRIPT} ${JSON_FILE} "
echo "" 
echo "Command Line: $CMD" | tee -a $log
echo "" 
echo "************************************************************************" | tee -a $log
echo ">>> CWLTOOL Logs start here "

$CMD >> $log  2>&1

#
echo ">>> CWLTOOL Logs end here " | tee -a ${log}
echo "Running sanity check" | tee -a ${log}
run_status=`getLogStatus ${log}`
echo "${run_status}" | tee -a $log
[ "${run_status}" != Success ] && exit 1
#
echo "" | tee -a ${log}
echo "Program complete - Check results under $sample_results_dir"| tee -a ${log}   
date
exit 0
