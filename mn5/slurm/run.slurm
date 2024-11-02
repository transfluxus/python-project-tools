#!/bin/bash

#SBATCH -n 1
#SBATCH -o %J.out
#SBATCH -e %J.err
#SBATCH -t 01:00
#SBATCH -A bsc100
#SBATCH --qos gp_bsccs

#module purge
module load intel impi
module load hdf5 mkl python #/3.12.1
#module miniconda/24.1.2

#python --version

cd /gpfs/home/bsc/bsc432917/projects/twitter_unpacker

python3 -m venv .venv
source .venv/bin/activate

echo "############"

python3 main.py
#python3 -m pip install --upgrade pip
#python3 -m pip install -r requirements-pip.txt

#hostname

cd /gpfs/home/bsc/bsc432917/slurm
mkdir -p "$SLURM_JOB_ID"
mv "$SLURM_JOB_ID.err" "$SLURM_JOB_ID/"
mv "$SLURM_JOB_ID.out" "$SLURM_JOB_ID/"