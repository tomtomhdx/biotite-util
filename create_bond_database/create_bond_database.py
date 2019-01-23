import argparse
from os.path import join
import concurrent.futures
import tarfile
import json
import os
import sys
import biotite
import biotite.structure.io.mmtf as mmtf


def mappable_create_bond_dict(file_names):
    global args
    try:
        with tarfile.open(args.archive, mode="r") as mmtf_archive:
            return create_bond_dict(mmtf_archive, file_names)
    except Exception as e:
        print(e, file=sys.stderr)
        return {}


def create_bond_dict(mmtf_archive, file_names):
    bond_dict = {}
    for file_name in file_names:
        mmtf_file = mmtf.MMTFFile()
        mmtf_file.read(mmtf_archive.extractfile(file_name))
        for group in mmtf_file["groupList"]:
            group_bonds = bond_dict.get(group["groupName"], {})
            bond_dict[group["groupName"]] = group_bonds
            # Each bond requires 2 entries in the list
            bond_index_list = group["bondAtomList"]
            bond_order_list = group["bondOrderList"]
            atom_name_list  = group["atomNameList"]
            for i in range(0, len(bond_index_list), 2):
                bond_i = bond_index_list[i]
                bond_j = bond_index_list[i+1]
                order = bond_order_list[i//2]
                key = frozenset(
                    (atom_name_list[bond_i], atom_name_list[bond_j], order)
                )
                if key in group_bonds:
                    group_bonds[key] += 1
                else:
                    group_bonds[key] = 1
    return bond_dict


def merge_bond_dicts(bond_dicts):
    merged_bond_dict = {}
    for bond_dict in bond_dicts:
        for group, group_bonds in bond_dict.items():
            merged_group_bonds = merged_bond_dict.get(group, {})
            merged_bond_dict[group] = merged_group_bonds
            for bond, count in group_bonds.items():
                if bond in merged_group_bonds:
                    merged_group_bonds[bond] += count
                else:
                    merged_group_bonds[bond] = count
    return merged_bond_dict


def filter_bond_dict(bond_dict, threshold):
    filtered_bond_dict = {}
    for group, group_bonds in bond_dict.items():
        filtered_group_bonds = {}
        for bond, count in group_bonds.items():
            if count >= threshold:
                filtered_group_bonds[bond] = count
        if len(filtered_group_bonds) > 0:
            filtered_bond_dict[group] = filtered_group_bonds
    return(filtered_bond_dict)


def write_bond_dict(bond_dict, json_file):
    json_bonds = {}
    for group, group_bonds in bond_dict.items():
        group_bond_list = []
        for bond in group_bonds:
            atoms_in_bond = []
            for item in bond:
                if isinstance(item, int):
                    order = item
                elif isinstance(item, str):
                    atoms_in_bond.append(item)
                else:
                    raise TypeError(
                        f"A bond tuple must not contain "
                        f"{type(item).__name__} objects"
                    )
            group_bond_list.append(atoms_in_bond)
        json_bonds[group] = group_bond_list
    json.dump(json_bonds, json_file, separators=(",", ":"))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a database, that contains the information which "
                    "atoms are connected in a given residue. "
                    "The information is based on a comprehensive archive "
                    "of MMTF files."
    )
    parser.add_argument(
        "archive",
        help="The path to the MMTF archive to be read."
    )
    parser.add_argument(
        "--outfile", "-o", default="bonds.json",
        help="The path to the file, where the output JSON should be placed. "
             "By default the file is placed in the current working directory."
    )
    parser.add_argument(
        "--threshold", "-t", default=0, type=int,
        help="A bond must at least have this many occurences to be considered "
             "in the output file. "
             "By default the threshold is 0."
    )
    parser.add_argument(
        "--chunksize", "-c", default=1000, type=int,
        help="The script is multiprocessed. This parameter gives the amount "
             "of files in the archive that is read and processed per process."
    )
    args = parser.parse_args()

    with tarfile.open(args.archive, mode="r") as mmtf_archive:
        members = mmtf_archive.getnames()
    members = members
    # Put files into approximatley evenly sized chunks
    # for multiprocessing
    chunks = []
    for i in range(0, len(members), args.chunksize):
        chunks.append(members[i : i+args.chunksize])
    with concurrent.futures.ProcessPoolExecutor() as executor:
        bonds_iterator = executor.map(mappable_create_bond_dict, chunks)
        bonds = merge_bond_dicts(bonds_iterator)
    bonds = filter_bond_dict(bonds, args.threshold)
    with open(args.outfile, "w") as json_file:
        write_bond_dict(bonds, json_file)