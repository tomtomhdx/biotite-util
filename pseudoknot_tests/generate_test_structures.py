import pandas as pd
import re
import argparse
import json
import numpy as np
import pickle as pkl
import biotite.structure as struc
BASES = 100
PAIRS = 20

def process(output):
    sample = list(range(1, BASES+1))
    basepairs = np.random.choice(sample, size=(PAIRS, 2), replace=False)
    pair = {}

    for basepair in basepairs:
        pair[basepair[0]] = basepair[1]
        pair[basepair[1]] = basepair[0]

    left_column = sample
    right_column = []
    for value in left_column:
        if value in pair:
            right_column.append(pair[value])
        else:
            right_column.append(0)
    columns = [left_column, ['N']*BASES, right_column]

    df = pd.DataFrame(columns)

    df.to_csv(f"{output}_knotted.bp", sep=' ', index=False, header=False)
    with open(f"{output}_knotted.pkl",'wb') as f:
        pkl.dump(basepairs, f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate test pairs"
    )
    parser.add_argument(
        "outfile",
        help="The path to the file, where the output JSON file should "
             "be placed."
    )
    args = parser.parse_args()

    process(args.outfile)

