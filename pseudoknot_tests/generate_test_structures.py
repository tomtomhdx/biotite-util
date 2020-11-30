import pandas as pd
import re
import argparse
import json
import numpy as np
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
    columns = {
        'col1': left_column,
        'col2': ['N']*BASES,
        'col3': right_column
    }
    print(columns)
    df = pd.DataFrame(columns)
    for row in df.iterrows():
        print(row)
    df.to_csv(output, sep=' ', index=False, header=False)
    solutions = set()
    for solution in struc.dot_bracket(basepairs - 1, BASES):
        solution = re.sub("[^().]", ".", solution)
        print(solution)
        solutions.add(solution)
    print("------------------------------------------------------------------")
    for solution in solutions:
        print(solution)
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

