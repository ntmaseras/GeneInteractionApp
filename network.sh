#!/bin/bash
#SBATCH --partition normal
#SBATCH -c 1
#SBATCH --account RNAMetabolism
#SBATCH --mem 30g
#SBATCH -t 10:00:00
#SBATCH --output=network_%j.out

python3 generate_network.py