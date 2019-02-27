from os.path import dirname
import os
import biotite.database.rcsb as rcsb

file_name = rcsb.fetch("1aki", "pdb", dirname(snakemake.output[0]))
os.rename(file_name, snakemake.output[0])