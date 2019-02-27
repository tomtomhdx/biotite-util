import biotite.structure.io.pdb as pdb
import biotite.structure as struc

pdb_file = pdb.PDBFile()
pdb_file.read(snakemake.input[0])
# Only use one model
structure = pdb_file.get_structure(model=1)
# Remove water
structure = structure[~struc.filter_solvent(structure)]
# Remove hydrogens
structure = structure[structure.element != "H"]
pdb_file.set_structure(structure)
pdb_file.write(snakemake.output[0])