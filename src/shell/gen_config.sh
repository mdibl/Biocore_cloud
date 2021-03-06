#
#What It Does: setup the expected directory structure for the results
# and generates the main config file(pipeline.cfg) for this project runID.
#
## Assumptions: assumes the following structure under the working directory
#   1) ../../cfgs
#   2) ../src
## Assumptions: assumes the following config files in the cfgs directory
#  1) biocore.cfg
#
#Usage:  run the command ./gen_config.sh to see the usage  
# 
#Organization: MDIBL
#Author: Lucie N. Hutchins
#Contact: lucie.hutchins@mdibl.org
#Modified: July 2019
#

source /etc/profile.d/biocore.sh

cd `dirname $0`
script_name=`basename $0`
## Check expected structure
working_dir=`pwd`
parent_dir=`dirname $working_dir`
cfg_dir_base=`dirname $parent_dir`
cfgs_dir=$cfg_dir_base/cfgs

##Matches team names  under /data/internal
PIPELINE_OWNER=$1
PROJECT_TEAM_NAME=$2
PROJECT_NAME=$3
ORGANISM=$4
REF_DATABASE=$5
REF_DATABASE_VERSION=$6
# transcriptome_joined = cat  *.rna *.ncrna
REF_DATASET=""
# Set the format of R1 and R2
READ1=""
READ2=""
## use {} to access the value of argument number > 9
CWL_SCRIPT=$7
PROJECT_PREFIX=`echo $PROJECT_NAME | cut -d '.' -f1`
#current_timestamp=${PROJECT_NAME}_$(date +%s)
current_timestamp=${PROJECT_PREFIX}.$(date +%s)
## Where we will store the pipeline meta config file for each sample
# name format sampleID.organism.pcf
PCF_BASE=$8
PCF_PROJECT_BASE=$PCF_BASE/${PROJECT_TEAM_NAME}/${PROJECT_NAME}/$current_timestamp
[ ! -d $PCF_PROJECT_BASE ] && mkdir -p $PCF_PROJECT_BASE
##We expect to find a json file for each sample under this path
# flename format sampleID.organism.json
JSON_BASE=$9
JSON_PROJECT_BASE=$JSON_BASE/${PROJECT_TEAM_NAME}/${PROJECT_NAME}/$current_timestamp
[ ! -d $JSON_PROJECT_BASE ] && mkdir -p $JSON_PROJECT_BASE
results_base=${10}
json_template=${11}
RESULTS_DIR_BASE=$results_base/${PROJECT_TEAM_NAME}/${PROJECT_NAME}
RESULTS_DIR=${RESULTS_DIR_BASE}/$current_timestamp

READS_BASE=${RESULTS_DIR_BASE}/reads

if [[ -z "$results_base" || ! -d $results_base ]]
then
   echo ""
   echo "****************************************************"
   echo "*      Project Main Config File Generator          *"
   echo "****************************************************"
   echo ""
   echo "What It Does: generates the main config file(pipeline.cfg) for this project runID."
   echo "This main config file sets global environment variables used by different downstream proccesses. "
   echo "The generated config file is stored under PIPELINE_RESULTS_BASE/PROJECT_TEAM_NAME/PROJECT_NAME/runID/cfgs/"
   echo ""
   echo "Usage: ./$script_name PIPELINE_OWNER PROJECT_TEAM_NAME PROJECT_NAME ORGANISM \
 REF_DATABASE REF_DATABASE_VERSION CWL_SCRIPT \
 PIPELINE_PCF_BASE PIPELINE_JSON_BASE PIPELINE_READS_BASE PIPELINE_RESULTS_BASE"
   echo ""
   echo "Where:"
   echo "    PIPELINE_OWNER:  The username for the owner of the pipeline results directory - Must be a valid username."
   echo "    PROJECT_TEAM_NAME: the team name associated with this project -  as found under /data/internal"
   echo "    PROJECT_NAME: The project name - as found under /data/internal/team_name/ - according to our standards"
   echo ""
   echo "    ORGANISM: The organism name - according to our standards"
   echo "    REF_DATABASE: The reference database source - according to our standards - see /data/external"
   echo "    REF_DATABASE_VERSION: The reference database version - example 95  for ensembl release 95"
   echo "    CWL_SCRIPT: full path to the cwl script to use for this pipeline"
   echo "    PIPELINE_PCF_BASE: pcf files base - according to our standards"
   echo "    PIPELINE_JSON_BASE: json files base  - according to our standards"
   echo "    PIPELINE_READS_BASE: input reads base - according to our standards"
   echo "    PIPELINE_RESULTS_BASE: results base - according to our standards"
   echo ""
   echo "Assumptions: assumes the following - relative to the script"
   echo "   1) ../../cfgs "
   echo "   2) ../../cfgs/biocore.cfg"
   echo ""
   echo "Example:"
   echo "    ./$script_name gmurray JimCoffman jcoffman_001.embryo_cortisol_2015 danio_rerio ensembl 93 \
    /opt/software/external/ggr-cwl/GGR-cwl/v1.0/RNA-seq_pipeline/pipeline-pe-unstranded-with-sjdb.cwl  \
    /data/projects/Biocore/biocore_analysis/biocore_projects/pipeline-runs-meta \
    /data/projects/Biocore/biocore_analysis/biocore_projects/rna-seq \
    /data/scratch/rna-seq  /data/scratch/rna-seq"
   echo ""
   exit 1
fi

## The master config file (pipeline.cfg) is run-specific
pipeline_config_base=${RESULTS_DIR}/cfgs
pipeline_cfg_file=$pipeline_config_base/pipeline.cfg
pipeline_json_template=$pipeline_config_base/template.json
## 
logs_base=${RESULTS_DIR}/logs
log_file=$logs_base/$script_name.log
git_base=""

if [[ $PIPELINE_PCF_BASE =~ .*($BIOCORE_PROJECTS_GIT_REPOS.*) ]] ; then
    git_base="${BASH_REMATCH[1]}"
fi

GIT_REPOS_PCF_BASE=$BIOCORE_PROJECTS_GIT_REPOS/`basename $PCF_BASE`/${PROJECT_TEAM_NAME}/${PROJECT_NAME}
GIT_REPOS_JSON_BASE=$BIOCORE_PROJECTS_GIT_REPOS/`basename $JSON_BASE`/${PROJECT_TEAM_NAME}/${PROJECT_NAME}

if [ ! -d $cfgs_dir ]
then
   echo "ERROR: Expected cfgs directory missing under $parent_dir"
   exit 1
fi
if [ ! -f $cfgs_dir/biocore.cfg ]
then
   echo "ERROR: Missing biocore.cfg under $cfgs_dir"
   exit 1
fi
[ ! -d $logs_base ] && mkdir -p $logs_base
[ ! -d $pipeline_config_base ] && mkdir -p $pipeline_config_base
[ -f $pipeline_cfg_file ] && rm -f $pipeline_cfg_file
[ -f $log_file ] && rm -f $log_file

touch $log_file
source  $cfgs_dir/biocore.cfg
#
#Project design file
ORIGINAL_READS_BASE=${BIOCORE_INFO_PATH[INTERNAL_DATA_BASE]}/${PROJECT_TEAM_NAME}/${PROJECT_NAME}
DESIGN_FILE=${ORIGINAL_READS_BASE}/${PROJECT_NAME}.design.txt
REF_DATA_BASE=${BIOCORE_INFO_PATH[SCRATCH_REF_BASE]}/$REF_DATABASE/$REF_DATABASE_VERSION

echo `date`>>$log_file

if [ ! -d  $ORIGINAL_READS_BASE ]
then
   echo "ERROR: Invalid Path to original reads - Expected $ORIGINAL_READS_BASE" | tee -a $log_file
   exit 1
fi
if [ ! -d  $REF_DATA_BASE ]
then
   echo "ERROR: Invalid Path to the reference data version - Expected $REF_DATA_BASE" | tee -a $log_file
   exit 1
fi
if [ ! -f $DESIGN_FILE ]
then
   echo "ERROR: Design file missing - expected: $DESIGN_FILE" | tee -a $log_file
   exit 1
fi
if [ ! -f $CWL_SCRIPT ]
then
   echo "ERROR: CWL Script missing - see $CWL_SCRIPT" | tee -a $log_file
   exit 1
fi
if [ ! -f $json_template ]
then
   echo "ERROR: json template missing - see $json_template" | tee -a $log_file
   exit 1
fi
##copy json template
cp $json_template $pipeline_json_template
##create the main pcf file
touch $pipeline_cfg_file
echo "###################################################" >> $pipeline_cfg_file
echo "## ${PROJECT_NAME} Pipeline Global Config File " >> $pipeline_cfg_file
echo "## " >> $pipeline_cfg_file
echo "## Date:`date` " >> $pipeline_cfg_file
echo "###################################################" >> $pipeline_cfg_file
echo "## Set path to local storage" >> $pipeline_cfg_file
for info_path in "${!BIOCORE_INFO_PATH[@]}"
do
    echo "export $info_path=${BIOCORE_INFO_PATH[$info_path]}">>$pipeline_cfg_file
done
echo "">>$pipeline_cfg_file
echo "## Set path to results">>$pipeline_cfg_file
echo "export RESULTS_DIR=$RESULTS_DIR">>$pipeline_cfg_file
echo "## Track the current runID">>$pipeline_cfg_file
echo "export RUN_ID=$current_timestamp">>$pipeline_cfg_file
echo "## Path to logs">>$pipeline_cfg_file
echo "export LOG_BASE=$logs_base">>$pipeline_cfg_file
echo "## Path to json template and pipeline.cfg">>$pipeline_cfg_file
echo "export CONFIG_BASE=$pipeline_config_base">>$pipeline_cfg_file
echo "## Set this pipeline ownership">>$pipeline_cfg_file
echo "export PIPELINE_OWNER=$PIPELINE_OWNER">>$pipeline_cfg_file
echo "## Set project info">>$pipeline_cfg_file
echo "export PROJECT_TEAM_NAME=$PROJECT_TEAM_NAME">>$pipeline_cfg_file
echo "export PROJECT_NAME=$PROJECT_NAME">>$pipeline_cfg_file
echo "">>$pipeline_cfg_file
echo "## Set path to cwl script - filename format: project_name.cwl">>$pipeline_cfg_file
echo "export CWL_SCRIPT=$CWL_SCRIPT">>$pipeline_cfg_file
echo "## Where we expect to fine the json template to use to generate sample-specific json files for this experiment">>$pipeline_cfg_file
echo "export JSON_TEMPLATE=$pipeline_json_template">>$pipeline_cfg_file
echo "## We expect to find a json file for each sample under this path">>$pipeline_cfg_file
echo "## filename format: sampleID.organism.json">>$pipeline_cfg_file
echo "export PATH2_JSON_FILES=$JSON_PROJECT_BASE">>$pipeline_cfg_file
echo "">>$pipeline_cfg_file
echo "## Where we will store the pipeline meta config file for each sample">>$pipeline_cfg_file
echo "## filename format:sampleID.organism.pcf">>$pipeline_cfg_file
echo "export PIPELINE_META_BASE=$PCF_PROJECT_BASE">>$pipeline_cfg_file
echo "">>$pipeline_cfg_file
echo "## Set Reference organism info">>$pipeline_cfg_file
echo "export ORGANISM=$ORGANISM">>$pipeline_cfg_file
echo "export REF_DATABASE=$REF_DATABASE">>$pipeline_cfg_file
echo "export REF_DATABASE_VERSION=$REF_DATABASE_VERSION">>$pipeline_cfg_file
echo "## Reference dataset used to generate indexes">>$pipeline_cfg_file
echo "export REF_DATASET=$REF_DATASET">>$pipeline_cfg_file
echo "">>$pipeline_cfg_file
echo "## Setup path sample reads and design file ">>$pipeline_cfg_file
echo "export ORIGINAL_READS_BASE=${ORIGINAL_READS_BASE}">>$pipeline_cfg_file
echo "export READS_BASE=${READS_BASE}">>$pipeline_cfg_file
echo "export DESIGN_FILE=${DESIGN_FILE}">>$pipeline_cfg_file
echo "">>$pipeline_cfg_file
echo "## Set the format of R1 and R2">>$pipeline_cfg_file
echo "declare -A READS">>$pipeline_cfg_file
echo "READS["1"]=\"$READ1\"">>$pipeline_cfg_file
echo "READS["2"]=\"$READ2\"">>$pipeline_cfg_file
echo "## Load sample IDs from the experiment design file into a container" >> $pipeline_cfg_file
echo "## Sample IDs are in the first column of the file" >> $pipeline_cfg_file
echo "declare -a SAMPLES" >> $pipeline_cfg_file

echo '[ -f $DESIGN_FILE ] && export SAMPLES=`cat $DESIGN_FILE | cut -f1 | sort | uniq`'>> $pipeline_cfg_file
echo "PIPELINE_CONFIG_FILE=$pipeline_cfg_file">>$log_file

echo "Program Complete">>$log_file
echo `date`>>$log_file
echo "$pipeline_cfg_file"
exit 0
