#!/bin/sh

date


if [ ! -f ${PIPELINE_METADATA_SCRIPT} ]
then
  echo "ERROR: The cwl file ${PIPELINE_METADATA_SCRIPT} - missing " 
  exit 1
fi

source ${PIPELINE_METADATA_SCRIPT} 

if [ ! -f ${CWL_SCRIPT} ]
then
  echo "ERROR: The cwl file ${CWL_SCRIPT} - missing " 
  exit 1
fi
if [ ! -f ${JSON_FILE} ]
then
  echo "ERROR: The json file ${JSON_FILE} - missing " 
  exit 1
fi
if [ ! ${PIPELINE_OWNER} ]
then
  echo "ERROR: pipeline ownership required - must specify PIPELINE_OWNER " 
  exit 1
fi

#set path to results 
results_base=`dirname ${JSON_FILE}`
results_dir=$results_base/results
[ ${RESULTS_DIR} ] && results_dir=${RESULTS_DIR}

param_log=$WORKSPACE/logs.sh
rm -f $param_log
touch $param_log

echo "CWL_SCRIPT=${CWL_SCRIPT}" | tee -a $param_log
echo "JSON_FILE=${JSON_FILE}" | tee -a $param_log
echo "CWL_COMMAND_OPTIONS=${CWL_COMMAND_OPTIONS}" | tee -a $param_log
echo "PIPELINE_OWNER=${PIPELINE_OWNER}" | tee -a $param_log
echo "RESULTS_DIR=${results_dir}" | tee -a $param_log

date

cat $param_log

echo "**************************"
echo "      System Dump         "
echo "**************************"

env

exit 0
