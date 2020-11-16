import argparse
import msgpack
import numpy as np
import biotite.structure as struc
import biotite.structure.io.pdbx as pdbx


BOND_ORDERS = {
    "SING" : struc.BondType.SINGLE,
    "DOUB" : struc.BondType.DOUBLE,
    "TRIP" : struc.BondType.TRIPLE,
    "QUAD" : struc.BondType.QUADRUPLE
}


def create_residue_dict(components_pdbx_file_path, msgpack_file_path):
    pdbx_file = pdbx.PDBxFile()
    pdbx_file.read(components_pdbx_file_path)
    components = pdbx_file.get_block_names()
    residue_dict = {}
    
    for i, component in enumerate(components):
        print(f"{component:3}   {int(i/len(components)*100):>3d}%", end="\r")
        try:
            # Some entries use invalid quotation for the component name
            cif_general = pdbx_file.get_category("chem_comp", block=component)
        except ValueError:
            cif_general = None
        cif_atoms = arrayfy(
            pdbx_file.get_category("chem_comp_atom", block=component)
        )
        cif_bonds = arrayfy(
            pdbx_file.get_category("chem_comp_bond", block=component)
        )
        if cif_atoms is None:
            continue

        array = struc.AtomArray(len(list(cif_atoms.values())[0]))

        array.res_name = cif_atoms["comp_id"]
        array.atom_name = cif_atoms["atom_id"]
        array.element = cif_atoms["type_symbol"]
        array.add_annotation("charge", int)
        array.charge = np.array(
            [int(c) if c != "?" else 0 for c in cif_atoms["charge"]]
        )
        if cif_general is None:
            array.hetero[:] = True
        else:
            array.hetero[:] = True if cif_general["type"] == "NON-POLYMER" \
                              else False
        
        # For some entries only 'model_Cartn',
        # for some entries only 'pdbx_model_Cartn_ideal' and
        # for some entries none of them is defined
        try:
            array.coord[:,0] = cif_atoms["pdbx_model_Cartn_x_ideal"]
            array.coord[:,1] = cif_atoms["pdbx_model_Cartn_y_ideal"]
            array.coord[:,2] = cif_atoms["pdbx_model_Cartn_z_ideal"]
        except (KeyError, ValueError):
            try:
                array.coord[:,0] = cif_atoms["model_Cartn_x"]
                array.coord[:,1] = cif_atoms["model_Cartn_y"]
                array.coord[:,2] = cif_atoms["model_Cartn_z"]
            except (KeyError, ValueError):
                # If none of them is defined, skip this component
                continue
            
        bonds = struc.BondList(array.array_length())
        if cif_bonds is not None:
            for atom1, atom2, order, aromatic_flag in zip(
                cif_bonds["atom_id_1"], cif_bonds["atom_id_2"],
                cif_bonds["value_order"], cif_bonds["pdbx_aromatic_flag"]
            ):
                atom_i = np.where(array.atom_name == atom1)[0][0]
                atom_j = np.where(array.atom_name == atom2)[0][0]
                if aromatic_flag == "Y":
                    bond_type = struc.BondType.AROMATIC
                else:
                    bond_type = BOND_ORDERS[order]
                bonds.add_bond(atom_i, atom_j, bond_type)
        array.bonds = bonds
        
        residue_dict[component] = array_to_dict(array)
    
    
    with open(msgpack_file_path, "wb") as msgpack_file:
        msgpack.dump(residue_dict, msgpack_file)



def arrayfy(category):
    if category is None:
        return None
    
    sample_value = list(category.values())[0]
    if isinstance(sample_value, str):
        # Single string -> single value -> convert each value to array
        arrayfied_category = {}
        for key, val in category.items():
            arrayfied_category[key] = np.array([val])
        return arrayfied_category
    else:
        # Looped values -> Already array
        return category


def array_to_dict(array):
    array_dict = {}

    array_dict["res_name"] = array.res_name.tolist()
    array_dict["atom_name"] = array.atom_name.tolist()
    array_dict["element"] = array.element.tolist()
    array_dict["charge"] = array.charge.tolist()
    array_dict["hetero"] = array.hetero.tolist()
    
    array_dict["coord_x"] = array.coord[:,0].tolist()
    array_dict["coord_y"] = array.coord[:,1].tolist()
    array_dict["coord_z"] = array.coord[:,2].tolist()
    
    bonds = array.bonds.as_array()
    array_dict["bond_i"] = bonds[:,0].tolist()
    array_dict["bond_j"] = bonds[:,1].tolist()
    array_dict["bond_type"] = bonds[:,2].tolist()

    return array_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a dataset containing MessagePack serialized "
                    "atom arrays for each PDB component."
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
    
    create_residue_dict(args.infile, args.outfile)