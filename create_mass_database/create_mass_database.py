import argparse
import msgpack
import biotite.structure.io.pdbx as pdbx


def create_mass_dict(components_pdbx_file_path, msgpack_file_path):
    pdbx_file = pdbx.PDBxFile()
    pdbx_file.read(components_pdbx_file_path)
    components = pdbx_file.get_block_names()
    mass_dict = {}
    for component in components:
        print(component)
        try:
            cif_dict = pdbx_file.get_category("chem_comp", block=component)
        except ValueError:
            # The 'chem_comp' category may contain unparsable names
            # with wrong quote escaping
            # In this case the PDBx file parser raises an Exception
            continue
        if cif_dict is None:
            # No info for this compound
            continue
        mass_dict[component] = float(cif_dict["formula_weight"])
    with open(msgpack_file_path, "wb") as msgpack_file:
        msgpack.dump(mass_dict, msgpack_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a database, that contains the masses of all "
                    "residues in the PDB."
                    "The information is based on a 'components.cif' file."
    )
    parser.add_argument(
        "infile",
        help="The path to the 'components.cif' file to be read."
    )
    parser.add_argument(
        "outfile",
        help="The path to the file, where the output MessagePack file should "
             "be placed."
    )
    args = parser.parse_args()

    create_mass_dict(args.infile, args.outfile)