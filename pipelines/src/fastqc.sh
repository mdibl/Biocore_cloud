##
## Assumptions: assumes the following structure under the  working directory
#   1) cfgs
#   2) src
## Assumptions: assumes the following config files in the cfgs directory
#  1) fastqc.tool_options.cfg
#  2) pipeline.cfg
#  3) reads both compressed and uncompressed
# 
source /etc/profile.d/biocore.sh 

TOOL_EXEC=`which fastqc`
date

if [ ! -f $TOOL_EXEC ]
then
  echo "ERROR: cutadapt NOT FOUND on server:`name -n`"
  exit 1
fi
#Show the version of the tool
TOOL_VERSION=fastqc-`$TOOL_EXEC --version| cut -d" " -f2`
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

if [ $# -lt 3 ]
then
  echo "************************************************"
  echo ""
  echo "Usage: ./$script_name  <READS_BASE> <READS_FORMAT> <RESULTS_BASE>"
  echo "Example: ./$script_name  /data/rna-seq/project1  fastq /path2/rna-seq/project1/results" 
  echo ""
  echo "************************************************"
  exit 1
fi
if [ ! -f $cfgs_dir/fastqc.tool_options.cfg ]
then
   echo "ERROR: Missing fastqc.tool_options.cfg under $cfgs_dir"
   exit 1
fi
if [ ! -f $cfgs_dir/pipeline.cfg ]
then
   echo "ERROR: Missing reads.cfg under $cfgs_dir"
   exit 1
fi
#Where to look for the reads
READS_BASE=$1
READS_FORMAT=$2
RESULTS_BASE=$3

source $cfgs_dir/fastqc.tool_options.cfg
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
   # get this sample reads files
   READ1=${READS["1"]}
   READ2=${READS["2"]}
   READ2_FILE=""
   READS_CMD=""
   READ1_FILE=$READS_BASE/`ls $READS_BASE/ | grep  $SAMPLE_ID$SAMPLE_READ_DELIMITER$READ1`
   if [ ! -f $READ1_FILE ]
   then
      echo "ERROR: $READ1_FILE NOT a file"
      continue
   fi
   ##detect type of reads: paired_end/single_end
   if [ ! -z "$READ2" ]
   then
       READ2_FILE=$READS_BASE/`ls $READS_BASE/ | grep  $SAMPLE_ID$SAMPLE_READ_DELIMITER$READ2`
       if [ ! -f $READ2_FILE ]
       then
            echo "ERROR: $READ2_FILE NOT a file"
            continue
       fi
       READS_CMD=" -t 2 $READ1_FILE $READ2_FILE"
    else
       READS_CMD=" -t 1 $READ1_FILE"
    fi
   # Set path to cmd
   CMD="$TOOL_EXEC -o $TOOL_RESULTS_DIR $FASTQC_CMD_OPTIONS -f $READS_FORMAT $READS_CMD"
   echo "##$SAMPLE_ID:" | tee -a $cmd_log_file
   echo "##$SAMPLE_ID:" | tee -a $log_file
   echo "start-time-`date`" | tee -a $log_file
   echo "$CMD" | tee -a $cmd_log_file
   $CMD  2>&1 | tee -a $log_file 
   echo "end-time-`date`" | tee -a $log_file
done
exit 0
