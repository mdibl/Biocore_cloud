#!/bin/sh

TRINOTATE_BASE=/opt/software/external/trinotate/Trinotate
SCRIPT_NAME=run_TrinotateWebserver.pl
PORT_NUMBER=80

if [ ! -f $TRINOTATE_BASE/$SCRIPT_NAME ]
then
	echo "Failed to start trinotateweb server - startup script Missing - see: $TRINOTATE_BASE/$SCRIPT_NAME"
	exit 1
fi
cd $TRINOTATE_BASE
sudo ./$SCRIPT_NAME $PORT_NUMBER

