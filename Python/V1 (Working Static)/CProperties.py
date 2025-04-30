###############################################################################
# Material Properties and Boundary Conditions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Fix the left-hand side of the plate in the X direction and set a
# force of 1 kN in the positive X direction.
#
import numpy as np
import random

def properties_and_BC(mapdl,servo_area_ids,DeviceWidth,Cell_width,Nside):
    print("Begining Properties and Boundry Condition Builder")
    # This example will use SI units.
    mapdl.units("SI")  # SI - International system (m, kg, s, K).

    # Define a material (nominal steel in SI)
    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

    for area_id in servo_area_ids:
        # Select the area
        mapdl.asel("S", "AREA", "", area_id)

        # Select nodes associated with that area
        mapdl.nsla("S", 1)  # 1 = select attached lines → areas
        mapdl.nsel("R", "LOC", "Z", 0)  # Only the top face nodes (if extruded along Z)

        # Create a component (optional, helps debugging later)
        mapdl.cm(f"servo_{area_id}", "NODE")

        # Apply random displacement in Z from -1 to 1
        disp = random.uniform(-1.0, 1.0)*0.05
        mapdl.d("ALL", "UZ", disp)

    # Clear selection
    mapdl.allsel()


    #BC
    XYSquareSelect(mapdl, "OuterEdges", 0, 0, DeviceWidth)

    # finally, be sure to select all nodes again to solve the entire solution
    mapdl.allsel(mute=True)

def XYSquareSelect(mapdl, label, x, y, Diam):
    mapdl.nsel("S", "LOC", "X", x + Diam / 2)
    mapdl.nsel("A", "LOC", "X", x - Diam / 2)
    mapdl.nsel("A", "LOC", "Y", y + Diam / 2)
    mapdl.nsel("A", "LOC", "Y", y - Diam / 2)
    mapdl.cm(cname=label)
    return label