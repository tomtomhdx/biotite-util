import argparse
import msgpack
import biotite.structure.io.pdbx as pdbx


def create_dict(components_pdbx_file_path, msgpack_file_path,
                subcategory, expected_type):
    pdbx_file = pdbx.PDBxFile()
    pdbx_file.read(components_pdbx_file_path)
    components = pdbx_file.get_block_names()
    mass_dict = {}
    for i, component in enumerate(components):
        print(f"{((i+1) / len(components) * 100):4.1f} %", end="\r")
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
        mass_dict[component] = expected_type(cif_dict[subcategory])
    print()
    with open(msgpack_file_path, "wb") as msgpack_file:
        msgpack.dump(mass_dict, msgpack_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a dataset, that maps component/residue names "
                    "to values of a given 'chem_comp' subcategory."
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
    parser.add_argument(
        "subcategory",
        help="The subcategory of the 'chem_comp' category."
    )
    parser.add_argument(
        "type",
        help="The type to use for the subcategory values. "
             "Either str, int or float. "
    )
    args = parser.parse_args()

    if args.type == "int":
        exp_type = int
    elif args.type == "float":
        exp_type = float
    elif args.type == "str":
        exp_type = str
    else:
        raise ValueError(f"'type' cannot be '{args.type}'")
    create_dict(args.infile, args.outfile, args.subcategory, exp_type)