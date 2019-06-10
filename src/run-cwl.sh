#!/bin/sh

CWLTOOL=`which cwltool`

CURRENT_USER=`id -un`
HOME=~
source /etc/profile.d/biocore.sh 

echo "`which fastqc`"
echo $PATH
date

if [ ! -f ${CWLTOOL} ]
then
  echo "ERROR: cwltool not installed on `uname -n ` - see ${CWLTOOL}" 
  exit 1
fi

if [ ! -f ${CWL_SCRIPT} ]
then
  echo "ERROR: The cwl file ${CWL_SCRIPT} - not found  on `uname -n ` " 
  exit 1
fi
if [ ! -f ${JSON_FILE} ]
then
  echo "ERROR: The json file ${JSON_FILE} - not found  on `uname -n ` " 
  exit 1
fi
if [ ! ${PIPELINE_OWNER} ]
then
  echo "ERROR: pipeline ownership required - must specify PIPELINE_OWNER " 
  exit 1
fi
#
#set path to pipeline-runs base
pipeline_runs_base=`dirname ${PIPELINE_METADATA_SCRIPT}`
failed_dir=$pipeline_runs_base/failed
launched_dir=$pipeline_runs_base/launched

#set path to results 
results_base=`dirname ${JSON_FILE}`
results_dir=$results_base/results
[ ${RESULTS_DIR} ] && results_dir=${RESULTS_DIR}


#
if [ -d $results_dir ]
then
   [ -d $results_dir.archive ] && sudo rm -rf  $results_dir.archive
   #[ "$(ls -A $results_dir)" ] && sudo mv $results_dir $results_dir.archive
   if [ "$(ls -A $results_dir)" ]
   then
       echo "SKIPPING: Pipeline results directory not empty - check $results_dir"
       exit 0
   fi
fi
#
[ ! -d $results_dir ] && sudo mkdir -p $results_dir
if [ ! -d $results_dir ]
then
   echo "ERROR: Failed to create $results_dir"
   exit 1
fi
## Set permissions on newly created directory
sudo chown $CURRENT_USER $results_dir
chmod 775 $results_dir
## Run the command under $results_dir
TOP=`pwd`

cd $results_dir
echo "***************** From `pwd` ******************"
echo "*" 
echo "* Running Command: $CWLTOOL $CWL_COMMAND_OPTIONS ${CWL_SCRIPT} ${JSON_FILE}"
echo "*"
echo "***************************************************************************"

$CWLTOOL $CWL_COMMAND_OPTIONS ${CWL_SCRIPT} ${JSON_FILE} 2>&1 

if [ $? -ne 0 ]
then
   echo "Command FAILED: '${CWLTOOL} ${CWL_COMMAND_OPTIONS} ${CWL_SCRIPT} ${JSON_FILE}' "
   sudo mv ${PIPELINE_METADATA_SCRIPT} $failed_dir/
   exit 1
fi
cd $TOP
##Set the ownership of the result to ${PIPELINE_OWNER}
sudo chown -R ${PIPELINE_OWNER} $results_dir
echo "Program complete - Check results under $results_dir"
## move this run mata script under 
sudo mv ${PIPELINE_METADATA_SCRIPT} $launched_dir/
date

echo "**************************"
echo "      System Dump         "
echo "**************************"

env

exit 0
