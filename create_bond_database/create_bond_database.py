import argparse
import json
import biotite.structure.io.pdbx as pdbx


BOND_ORDERS = {
    "SING" : 1,
    "DOUB" : 2,
    "TRIP" : 3,
    "QUAD" : 4
}


def create_bond_dict(components_pdbx_file_path, json_file_path):
    pdbx_file = pdbx.PDBxFile()
    pdbx_file.read(components_pdbx_file_path)
    components = pdbx_file.get_block_names()
    bond_dict = {}
    for component in components:
        print(component)
        cif_bonds = pdbx_file.get_category("chem_comp_bond", block=component)
        if cif_bonds is None:
            # No bond info for this compound
            continue
        if isinstance(cif_bonds["comp_id"], str):
            # Single string -> single bond
            group_bonds = {
                " ".join(
                    (cif_bonds["atom_id_1"], cif_bonds["atom_id_2"])
                ) : BOND_ORDERS[cif_bonds["value_order"]]
            }
        else:
            # Looped values -> multiple bonds
            group_bonds = {
                " ".join((atom1, atom2)) : BOND_ORDERS[order]
                for atom1, atom2, order
                in zip(
                    cif_bonds["atom_id_1"],
                    cif_bonds["atom_id_2"],
                    cif_bonds["value_order"]
                )
            }
        bond_dict[component] = group_bonds
    with open(json_file_path, "w") as json_file:
        json.dump(bond_dict, json_file, separators=(",", ":"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a database, that contains the information which "
                    "atoms are connected in a given residue. "
                    "The information is based on a 'components.cif' file."
    )
    parser.add_argument(
        "infile",
        help="The path to the 'components.cif' file to be read."
    )
    parser.add_argument(
        "outfile",
        help="The path to the file, where the output JSON should be placed."
    )
    args = parser.parse_args()

    create_bond_dict(args.infile, args.outfile)