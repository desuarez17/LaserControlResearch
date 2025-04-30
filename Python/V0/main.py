#This Organizes the specified sub calls for each ANSYS build step
import numpy as np
from ansys.mapdl.core import launch_mapdl
import CGeometry
import CMesh
import CProperties
import CResults

notch_radius = 0.01
thickness = 0.01
width = 0.1
length = 0.4


def main(mapdl):
    try:
        # Build plate Geometry wit specfied faces
        CGeometry.platebuilder(mapdl, thickness=thickness, width=width, length=length)
        CMesh.platemesh(mapdl, notch_radius, thickness=thickness)
        CProperties.properties_and_BC(mapdl, width=width, length=length)

        # Solve the Static Problem
        # ~~~~~~~~~~~~~~~~~~~~~~~~
        # Solve the static analysis
        mapdl.run("/SOLU")
        mapdl.antype("STATIC")
        mapdl.solve()
        mapdl.finish(mute=True)

        #Show max Stress
        result = mapdl.result
        result.plot_principal_nodal_stress(
            0,
            "SEQV",
            lighting=False,
            background="w",
            show_edges=True,
            text_color="k",
            add_text=False,
        )

        # Close Mechanical
        mapdl.exit()
    except Exception as e:
        print(f"Caught error: {e}")
        # Close Mechanical
        mapdl.exit()

if __name__ == "__main__":
    # start mapdl (Ansys)
    mapdl = launch_mapdl(loglevel="ERROR")

    main(mapdl)

    # Close Mechanical
    mapdl.exit()