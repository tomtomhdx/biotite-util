import argparse
from os.path import join
import tarfile
import json
import os
import sys
import biotite
import biotite.structure.io.mmtf as mmtf


def create_bond_dict(mmtf_archive, file_name):
    bonds = {}
    for pdb_id in pdb_ids:
        mmtf_file = mmtf.MMTFFile()
        mmtf_file.read(mmtf_archive.extractfile(file_name))
        for group in mmtf_file["groupList"]:
            group_bonds = bonds.get(group["groupName"])
            if group_bonds is None:
                # Group has not been recorded yet
                group_bonds = {}
                bonds[group["groupName"]] = group_bonds
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
        #print(pdb_id)
        #for group in mmtf_file["groupList"]:
        #    if group["groupName"] == "MET":
        #        print(group["groupName"])
        #        print(group)
        #        print()
        #print()
    #print("\n"*2)
    #for key, val in bonds.items():
    #    print(key)
    #    print(val)
    #    print()
    return bonds


def merge_bond_dicts()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a database, that contains the information which "
                    "atoms are connected in a given residue. "
                    "The information is based on a comprehensive archive "
                    "of MMTF files."
    )
    parser.add_argument(
        "archive",
        help="The MMTF archive to be read"
    )
    parser.add_argument(
        "--dir",  "-d", dest="directory", default=".",
        help="the Biotite project directory to put the database into."
    )
    parser.add_argument(
        "--threshold",   "-i",
        help="This percentage of residues must have a certain bond "
             "for this bond to be considered."
    )
    #args = parser.parse_args()

mmtf_archive_path = "/home/kunzmann/Documents/mmtf_20180918.tar"
with tarfile.open(mmtf_archive_path, mode="r") as mmtf_archive:
    members = mmtf_archive.getnames()
    members = members[:10]
    bonds1 = create_bond_dict(mmtf_archive, members[:5])
    bonds2 = create_bond_dict(mmtf_archive, members[5:])
with open("test.json", "w") as json_file:
    json.dump(bonds, json_file, indent=4)