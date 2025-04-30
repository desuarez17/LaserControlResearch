###############################################################################
# Material Properties and Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fix the left-hand side of the plate in the X direction and set a
# force of 1 kN in the positive X direction.
#
import numpy as np

def properties_and_BC(mapdl,width=1,length=1):
    print("Begining Properties and Boundry Condition Builder")
    # This example will use SI units.
    mapdl.units("SI")  # SI - International system (m, kg, s, K).

    # Define a material (nominal steel in SI)
    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

    # Fix the left-hand side.
    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "UX")

    # Fix a few nodes on the left-hand side of the plate in the Y and Z
    # direction.  Otherwise, the mesh would be allowed to move in the y
    # direction and would be an improperly constrained mesh.
    mapdl.nsel("R", "LOC", "Y", width / 2)
    mapdl.d("ALL", "UY")
    mapdl.d("ALL", "UZ")

    # Apply a force on the right-hand side of the plate.  For this
    # example, we select the nodes at the right-most side of the plate.
    mapdl.nsel("S", "LOC", "X", length)

    # Verify that only the nodes at length have been selected:
    # assert np.unique(mapdl.mesh.nodes[:, 0]) == length

    # Next, couple the DOF for these nodes.  This lets us provide a force
    # to one node that will be spread throughout all nodes in this coupled
    # set.
    mapdl.cp(5, "UX", "ALL")

    # Select a single node in this set and apply a force to it
    # We use "R" to re-select from the current node group
    mapdl.nsel("R", "LOC", "Y", width / 2)  # selects more than one
    single_node = mapdl.mesh.nnum[0]
    mapdl.nsel("S", "NODE", vmin=single_node, vmax=single_node)
    mapdl.f("ALL", "FX", 1000)

    # finally, be sure to select all nodes again to solve the entire solution
    mapdl.allsel(mute=True)