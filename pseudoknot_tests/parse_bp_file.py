import pandas as pd
import re
import argparse
import json
import numpy as np
import pickle as pkl
import biotite.structure as struc

def process(input_file, output_file):
    df = pd.read_csv(input_file, sep=" ")
    pairs = set()
    for i, row in df.iterrows():
        pos = row[0]
        pair = row[-1]
        if pair == 0:
            continue
        pairs.add(sorted((pair, pos)))
    basepairs = np.zeros((len(pairs), 2))
    for row, basepair in zip(basepairs, pairs):
        row = basepair
    with open(f"{output}.pkl",'wb') as f:
        pkl.dump(basepairs, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate test pairs"
    )
    parser.add_argument(
        "infile",
        help="The path to the file, where the output JSON file should "
             "be placed."
    )
    parser.add_argument(
        "outfile",
        help="The path to the file, where the output JSON file should "
             "be placed."
    )
    args = parser.parse_args()

    process(args.infile, args.outfile)

