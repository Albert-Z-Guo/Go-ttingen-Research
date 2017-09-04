#!/bin/bash
#
#$ -l cvmfs
#$ -l h_rt=24:00:00
#$ -l h_vmem=8G
#$ -j y

SCRIPT_PATH=$1
SCRIPT_NAME=$2

echo "=================================================="
echo " cd "$SCRIPT_PATH
echo "=================================================="
cd $SCRIPT_PATH
echo "=================================================="
echo " source env.sh"
echo "=================================================="
source env.sh
echo "=================================================="
echo " python "$SCRIPT_NAME
echo "=================================================="
python $SCRIPT_NAME
