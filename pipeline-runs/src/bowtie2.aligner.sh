##
## Assumptions: assumes the following structure under the  working directory
#   1) cfgs
#   2) src
## Assumptions: assumes the following config files in the cfgs directory
#  1) bowtie2.aligner_options.cfg
#  2) pipeline.cfg
# 
source /etc/profile.d/biocore.sh

TOOL_EXEC=`which bowtie2`
date

if [ ! -f $TOOL_EXEC ]
then
  echo "ERROR: bowtie2 NOT installed on server:`name -n`"
  exit 1
fi
#Show the version of the tool
TOOL_VERSION=bowtie2-`$TOOL_EXEC --version| grep bowtie2 | cut -d " " -f 3`

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
  echo "Bowtie2 Version to use: $TOOL_VERSION"
  echo "Usage: ./$script_name <TOOL_REF_INDEX> <READS_BASE> <RESULTS_BASE>"
  echo "Where TOOL_REF_INDEX is the path2 bowtie2 reference indexes generated using $TOOL_VERSION"
  echo "Example: ./$script_name path2ref_index/index_prefix /data/rna-seq/project1 \
 /results/rna-seq/project1" 
  echo ""
  echo "************************************************"
  exit 1
fi
if [ ! -f $cfgs_dir/bowtie2.aligner_options.cfg ]
then
   echo "ERROR: Missing bowtie2.aligner_options.cfg under $cfgs_dir"
   exit 1
fi
if [ ! -f $cfgs_dir/pipeline.cfg ]
then
   echo "ERROR: Missing pipeline.cfg under $cfgs_dir"
   exit 1
fi
TOOL_REF_INDEX=$1
#Where to look for the reads
READS_BASE=$2
RESULTS_BASE=$3

source ../cfgs/bowtie2.aligner_options.cfg
source ../cfgs/pipeline.cfg

#Where to look for bowtie2 ref indexes
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

# sample reads filename info
for SAMPLE_ID in $SAMPLES
do
   # get this sample reads files
   READ1=${READS["1"]}
   READ2=${READS["2"]}
   READ2_FILE=""
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
       READ1=" -1 $READ1_FILE"
       READ2=" -2 $READ2_FILE"
    else
       READ1=" -U $READ1_FILE"  
    fi
   # Set path to results
   RESULTS_FILE=$TOOL_RESULTS_DIR/$SAMPLE_ID.sam

   CMD="$TOOL_EXEC $ALIGNER_CMD_OPTIONS $TOOL_REF_INDEX  $READ1 $READ2 -S $RESULTS_FILE"
   echo "##$SAMPLE_ID:" | tee -a $cmd_log_file
   echo "##$SAMPLE_ID:" | tee -a $log_file
   echo "start-time-`date`" | tee -a $log_file
   echo "$CMD" | tee -a $cmd_log_file
   $CMD  2>&1 | tee -a $log_file 
   echo "end-time-`date`" | tee -a $log_file
done
exit 0
