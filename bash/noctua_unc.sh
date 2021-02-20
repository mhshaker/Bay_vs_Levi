#!/bin/bash
#SBATCH -N 1
#SBATCH -J test_shaker
#SBATCH -A hpc-prf-isys
#SBATCH -p batch
#SBATCH --mail-type all
#SBATCH --mail-user mhshaker@mail.upb.de

module add singularity
for ((idx=$1; idx<$2; ++idx)); do
    singularity run --bind /upb/scratch/departments/pc2/groups/hpc-prf-isys/mhshaker/:/upb/scratch/departments/pc2/groups/hpc-prf-isys/mhshaker/ /upb/scratch/departments/pc2/groups/hpc-prf-isys/mhshaker/s_python3.simg python3 Uncertainty.py $idx
    echo job_id $idx Done
done

