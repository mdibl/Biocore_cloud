#!/bin/bash

#A script to push local production updates onto remote github repository.
# Runs as cron on local server
#
# Usage: ./script_name git_repos_name
# 
# What it does:"
# 1) Clones a fresh copy of the repository
# 2) Synches production copy to the clonned repository
# 3) Pushes updates to remote if detected
#
#Organization: MDIBL
#Author: Lucie N. Hutchins
#Contact: lucie.hutchins@mdibl.org
#Modified: September 2019
#

script_name=`basename $0`
cd `dirname $0`
working_dir=`pwd`
repos_name=$1

source ~/.bashrc

LOG_BASE=$LOGS_BASE
CLONE_REPOS_BASE=$GIT_CLONE_BASE
## Check expected structure
parent_dir=`dirname $working_dir`
python_dir=$parent_dir/python
rsync_script=$python_dir/rsync_directories.py

#default git clone base to working directory
[ -z "$GIT_CLONE_BASE" ] && CLONE_REPOS_BASE=$working_dir
if [ -z "$repos_name" ]
then
  echo ""
  echo "************************************************************************"
  echo "************************************************************************"
  echo "A script to push local production updates onto remote github repository."
  echo ""
  echo "Usage: ./$script_name git_repos_name"
  echo "Where git_repos_name is the name of the github repository you want to update."
  echo ""
  echo "What it does:"
  echo "1) Clones a fresh copy of the repository"
  echo "2) Synched production to the clonned repository"
  echo "3) Pushes updates to remote if detected"
  echo ""
  echo "Note:"
  echo "The script assumes GIT_CLONE_BASE and LOG_BASE global environment varialble set in .bashrc"
  echo "If these two are not set then the working directory is used as the base."
  echo ""
  exit 1
fi
LOG_BASE=$LOGS_BASE/$repos_name
[[ ! -z "$LOG_BASE" &&  ! -d $LOG_BASE ]] && mkdir -p $LOG_BASE
[ ! -d $CLONE_REPOS_BASE ] && mkdir -p $CLONE_REPOS_BASE 

log_file=$LOG_BASE/$script_name.log
#default log base to working directory
[ -z "$LOG_BASE" ] && log_file=$script_name.log 
touch $log_file

git_prog=`which git`
if [ ! -f $git_prog ]
then
   echo $git_prog
   echo "'git' not installed on `uname -n`"
   exit 1
fi
python_prog=`which python`
if [ ! -f $python_prog ]
then
   echo "'python' not installed on `uname -n`"
   exit 1
fi
rsync_prog=`which rsync`
if [ ! -f $rsync_prog ]
then
   echo "'rsync' not installed on `uname -n`"
   exit 1
fi
if [ ! -f $rsync_script ]
then
  echo "ERROR:$rsync_script is expected"
  exit 1
fi

cd $CLONE_REPOS_BASE
[ -d $repos_name ] && rm -rf $repos_name
$git_prog clone https://$GIT_TOKEN@$GIT_URL/$GIT_ORG/$repos_name.git 
echo "===== Date: `date` =======">>$log_file

if [ ! -d $repos_name ]
then
  echo "ERROR: Failed to clone $repos_name under $CLONE_REPOS_BASE" >> $log_file
  echo "Cmd: $git_prog clone https://$GIT_TOKEN@$GIT_URL/$GIT_ORG/$repos_name.git"
  exit 1
fi
# rsync production to the cloned copy
$python_prog $rsync_script -s $BC_PROD_BASE/$repos_name -d $CLONE_REPOS_BASE/$repos_name >> $log_file 2>&1

cd $CLONE_REPOS_BASE/$repos_name
# push local updates to remote if detected
#
git_fetch=$(git status | grep "working tree clean"  2>&1)
if [ -z "$git_fetch" ]
then
   echo "Changes detected: Pushing new changes to remote " | tee -a $log_file
   $git_prog add -A >> $log_file 2>&1
   $git_prog pull >> $log_file 2>&1
   $git_prog commit -m"$repos_name update as of `date`" >> $log_file 2>&1
   $git_prog push >>$log_file 2>&1
   echo"">>$log_file
   echo "**************************************" >>$log_file
else
   echo "Repos: $repos_name up to date with remote origin" >>$log_file
fi
