#!/bin/sh


#rsync_options="--links --ignore-errors"
# make sure the connection is passwordless between the host
# and the destination server - 
# https://www.centos.org/docs/5/html/5.1/Deployment_Guide/s3-openssh-dsa-key.html
# A trailing slash on the source changes this behavior to avoid creating 
# an additional directory level at the destination. You can think of a trailing / 
# on a source as meaning "copy the contents of this directory" as opposed 
# to "copy the directory by name",

SCRIPT_NAME=`basename $0`

#rsync_options=' -avz  --rsync-path="/usr/bin/sudo /usr/bin/rsync" --exclude=.snapshot'
rsync_options=' -avz  --exclude=.snapshot --exclude=results --exclude=logs'
rsync_prog=`which rsync`
if [ ! -f $rsync_prog ]
then
   echo $rsync_prog
   echo "'rsync' not installed on `uname -n`"
   exit 1
fi

#Check the number of arguments
if [ $# -lt 2 ]
then
  echo ""
  echo "***********************************************"
  echo "Bad usage ---"
  echo "Usage: ./$SCRIPT_NAME  LOCAL_DIR REMOTE_DIR"
  echo "Example1: ./$SCRIPT_NAME  /opt/software /s3-drives/biocore-software"
  echo ""
  echo "***********************************************"
  echo ""
  exit 1
fi
src_dir="$1"
dest_dir="$2"
[ ! -d $dest_dir ] && mkdir -p $dest_dir

## rsync /opt/software
echo " Running: $rsync_prog $rsync_options $src_dir $dest_dir"
$rsync_prog $rsync_options $src_dir $dest_dir 
if [ $? -ne 0 ]
then
   echo "Cmd: rsync $rsync_options $src_dir $dest_dir - FAILED"
   exit 1
fi
exit 0
