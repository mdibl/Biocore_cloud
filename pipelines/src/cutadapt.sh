##
## Assumptions: assumes the following structure under the  working directory
#   1) cfgs
#   2) src
## Assumptions: assumes the following config files in the cfgs directory
#  1) cutadapt.tool_options.cfg
#  2) pipeline.cfg
# 
source /etc/profile.d/biocore.sh 

TOOL_EXEC=`which cutadapt`
date

if [ ! -f $TOOL_EXEC ]
then
  echo "ERROR: cutadapt NOT FOUND on server:`name -n`"
  exit 1
fi
#Show the version of the tool
TOOL_VERSION=cutadapt-v`$TOOL_EXEC --version`

cd `dirname $0`
script_name=`basename $0`
## Check expected structure
working_dir=`pwd`
parent_dir=`dirname $working_dir`
cfgs_dir=$parent_dir/cfgs

if [ ! -d $cfgs_dir ]
then
   echo "ERROR: Expected cfgs directory missing under $parent_dir"
   exit 1
fi

if [ $# -lt 2 ]
then
  echo "************************************************"
  echo ""
  echo "Usage: ./$script_name  <READS_BASE> <RESULTS_BASE>"
  echo "Example: ./$script_name  /data/rna-seq/project1  /results/rna-seq/project1" 
  echo ""
  echo "************************************************"
  exit 1
fi
if [ ! -f $cfgs_dir/biocore.cfg ]
then
   echo "ERROR: Missing biocore.cfg under $cfgs_dir"
   exit 1
fi
if [ ! -f $cfgs_dir/cutadapt.tool_options.cfg ]
then
   echo "ERROR: Missing cutadapt.tool_options.cfg under $cfgs_dir"
   exit 1
fi
if [ ! -f $cfgs_dir/reads.cfg ]
then
   echo "ERROR: Missing reads.cfg under $cfgs_dir"
   exit 1
fi
#Where to look for the reads
READS_BASE=$1
RESULTS_BASE=$2

source $cfgs_dir/cutadapt.tool_options.cfg
source $cfgs_dir/pipeline.cfg
#Where to store the alignment results
TOOL_RESULTS_DIR=$RESULTS_BASE/$TOOL_VERSION
RESULTS_LOG_DIR=$RESULTS_BASE/logs

[ ! -d $TOOL_RESULTS_DIR ]&& mkdir -p $TOOL_RESULTS_DIR
[ ! -d $RESULTS_LOG_DIR ]&& mkdir -p $RESULTS_LOG_DIR
cmd_log_file=$RESULTS_LOG_DIR/$script_name.cmds.log
log_file=$RESULTS_LOG_DIR/$script_name.log
rm -f $cmd_log_file
rm -f $log_file
touch $cmd_log_file
touch $log_file

#
# sample reads filename info
#READS_FILE_SUFFIX=noadapt.fastq.gz
for SAMPLE_ID in $SAMPLES
do
   # get this sample reads files
   echo "##$SAMPLE_ID:" | tee -a $cmd_log_file
   echo "##$SAMPLE_ID:" | tee -a $log_file
   echo "start-time-`date`" | tee -a $log_file
   declare -a reads
   reads=`ls $READS_BASE/ | grep  $SAMPLE_ID$SAMPLE_READ_DELIMITER`
   for read_file in $reads
   do
       # Set path to results
       RESULTS_FILE=$TOOL_RESULTS_DIR/$read_file
       INPUT_READS_FILE=$READS_BASE/$read_file
       [ ! -f $INPUT_READS_FILE ] && continue
       #Usage: cutadapt -b adapter_seq  -o out.fastq.gz in.fastq.gz
       CMD="$TOOL_EXEC $CUTADAPT_CMD_OPTIONS -o $RESULTS_FILE $INPUT_READS_FILE"
       echo "$CMD" | tee -a $cmd_log_file
       $CMD  2>&1 | tee -a $log_file 
       echo "end-time-`date`" | tee -a $log_file
   done
   echo "end-time-`date`" | tee -a $log_file
done
exit 0
