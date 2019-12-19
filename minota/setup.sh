#!/bin/sh

cd `dirname $0`
if [ ! -f ./config/biocore.cfg ]
then
   echo "ERROR: ./config/biocore.cfg not found "
   exit 1

fi
WS_USER_NAME=$1

if [ -z "$WS_USER_NAME" ]
then
   echo ""
   echo "Usage: ./setup.sh user_name"
   echo "Where: user_name is a word composition of your first name and the  "
   echo "       first character of your last name - all in lowercase. "
   echo "       For example: the user_name for Lucie Hutchins would be lucieh "
   echo ""
   exit 1
fi

source ./config/biocore.cfg
source ./config/.users.cfg

##Create user's working directory under
## ec2-user's home -- 
S3_USER_BASE=$MINOTA_BASE/$WS_USER_NAME
USER_BASE=~/$WS_USER_NAME
if [ ${USERS[$WS_USER_NAME]+abc} ]
then
   [ ! -d $USER_BASE ] && mkdir $USER_BASE
   [ ! -d $S3_USER_BASE ] && mkdir $S3_USER_BASE
   user_name=${USERS[$WS_USER_NAME]}
   mkdir $USER_BASE/workshop_src
   cp -R tools/*  $USER_BASE/workshop_src/
   echo "**********************************************"
   echo ""
   echo "$user_name, Welcome to MINOTA 2019!"
   echo "" 
   echo "**********************************************"
   echo "Please Note:"
   echo "Your working directory is: $USER_BASE"
   echo "Your local copy of workshop Scripts: $USER_BASE/workshop_src "
   echo ""
   echo "To get started, next run the command: cd $USER_BASE "
   echo ""
   echo "And Voila!"
   echo ""
   echo "FYI:"
   echo "$USER_BASE is not a persistent storage - will be destroyed if the machine is terminated."
   echo "However, you can make $USER_BASE persistent by copying its content to $S3_USER_BASE"
   echo ""
else
   echo "Bad username:$WS_USER_NAME - Check that your username is all in lowercase and follow the format: " 
   echo "first_name followed by the first character of your last_name"
   exit 1
fi

exit 0

