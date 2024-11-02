#!/bin/bash

SBATCH -n 1
SBATCH -o %J.out
SBATCH -e %J.err
SBATCH -t 01:00
SBATCH -A bsc100
SBATCH --qos gp_bsccs

hostname
echo $SLURM_JOB_ID
echo "done!"