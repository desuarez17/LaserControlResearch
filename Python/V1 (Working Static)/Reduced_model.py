#This Organizes the specified sub calls for each ANSYS build step
from cProfile import label

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from ansys.mapdl.core import launch_mapdl
import CGeometry
import CMesh
import CProperties
import CResults

Nside = 5;#Number of servos per side
Servo_width = 0.1#size of each servo area
DeviceWidth = 1;
Cell_width = DeviceWidth/Nside;
thickness = 0.05

def main(mapdl):
    try:
        mapdl.prep7()
        mapdl.blc5(0, 0, width=DeviceWidth, height=DeviceWidth, depth=thickness)  # main area
        mapdl.et(1,"SOLID186")

        mapdl.mshkey(0)
        mapdl.mshape(1,"3D")
        #mapdl.SMRT(6)
        mapdl.vsweep("all")
        mapdl.eplot(vtk=True, show_edges=True, show_axes=False, line_width=2, background="w")

        # Confirm mesh creation
        print("Nodes:", mapdl.mesh.n_node)
        print("Elements:", mapdl.mesh.n_elem)



        # Select nodes on the right face (X = DeviceWidth)
        tol = 1e-1

        def XYSquareSelect(mapdl,label, x, y, Diam,thickness = np.nan):
            mapdl.allsel(mute=True)
            mapdl.nsel("S", "LOC", "X", x - Diam / 2,x + Diam / 2)#Select line
            mapdl.nsel("R", "LOC", "Y", y - Diam / 2,y + Diam / 2)
            mapdl.cm('outer_sq', 'NODE')
            if thickness != np.nan:
                mapdl.nsel("S", "LOC", "X", x - Diam / 2 + thickness, x + Diam / 2 - thickness)  # Select Inner area
                mapdl.nsel("R", "LOC", "Y", y - Diam / 2 + thickness, y + Diam / 2 - thickness)
                mapdl.cm('inner_sq', 'NODE')
                #Take diffrence of square areas
                mapdl.cmsel('S', 'outer_sq', 'NODE')
                mapdl.cmsel('U', 'inner_sq', 'NODE')

            mapdl.cm(label,"NODE")
            return label

        def ConstrainNodes(mapdl,label, x, y, Diam,Z_displacment,IncludeInner=True,plotme=False,FixedEdge=False):
            if IncludeInner:
                XYSquareSelect(mapdl,label, x, y, Diam)
            else:
                XYSquareSelect(mapdl, label, x, y, Diam, 0.025)

            mapdl.cmsel("s", label, 'NODE')
            if FixedEdge:
                mapdl.d('ALL', 'UX', 0)
                mapdl.d('ALL', 'UY', 0)
            mapdl.d('ALL', 'UZ', Z_displacment)
            this_nodelist = mapdl.mesh.nodes
            this_nodelist[:, 2] = Z_displacment

            if plotme:
                mapdl.nplot(vtk=True, show_node_numbering=True, color="green", point_size=10, background="w")
            return this_nodelist
        # OuterEdgesLabel = XYSquareSelect(mapdl,"OuterEdges",0,0,DeviceWidth)
        # mapdl.cmsel("ALL",OuterEdgesLabel)
        # mapdl.d("ALL","ALL",0)

        constrained_nodes = []

        #Constrain outside
        OuterNodeList = ConstrainNodes(mapdl, 'Outside', 0, 0, DeviceWidth,0,IncludeInner=False,plotme=False,FixedEdge=True)

        # Servo Displace
        ServoNodeList = ConstrainNodes(mapdl, 'InnerPoint',0.25, 0.25, Servo_width,  0.4, IncludeInner=True, plotme=False)

        ConstrainedNodes = np.vstack((OuterNodeList,ServoNodeList))
        #solve1
        mapdl.allsel(mute=True)

        # nnum, coords = mapdl.mesh.nnum, mapdl.mesh.nodes
        #
        # # 2. Build color array
        # colors = np.zeros_like(nnum)
        # print(constrained_nodes)
        # for i, node in enumerate(nnum):
        #     if node in constrained_nodes:
        #         colors[i] = 1  # constrained
        #     else:
        #         colors[i] = 0  # free

        # Editable colormap
        coords = mapdl.mesh.nodes

        # --- plot ---
        fig, ax = plt.subplots()

        # 1. Plot all nodes grey
        ax.scatter(coords[:, 0], coords[:, 1], color='lightgrey', s=10)

        # 2. Plot constrained nodes with color
        sc = ax.scatter(ConstrainedNodes[:, 0], ConstrainedNodes[:, 1], c=ConstrainedNodes[:,2], cmap='turbo', s=10)

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Constraints Visualization')
        plt.axis('equal')
        plt.legend()
        plt.show()


        # This example will use SI units.
        mapdl.units("SI")  # SI - International system (m, kg, s, K).

        # Define a material (nominal steel in SI)
        mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
        mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
        mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

        mapdl.run("/SOLU")
        mapdl.antype("STATIC")
        mapdl.time(1)
        mapdl.solve()
        mapdl.finish(mute=True)

        # Make sure solution is done
        mapdl.post1()
        mapdl.set(1)  # first load step

        # now plot nodal Z displacement (DOF = UZ)
        mapdl.plnsol('UZ')

        # Show max Stress
        # result = mapdl.result
        # result.plot_principal_nodal_stress(
        #     0,
        #     "SEQV",
        #     lighting=False,
        #     background="w",
        #     show_edges=True,
        #     text_color="k",
        #     add_text=False,
        # )

        mapdl.exit()
    except Exception as e:
        print(f"Caught error: {e}")

        # Close Mechanical
        mapdl.exit()

if __name__ == "__main__":
    # start mapdl (Ansys)
    mapdl = launch_mapdl(run_location=r"C:\Users\damia\OneDrive\Desktop\drive\School Vault\RIT\Research\Ansys\MAPDL_FILES", additional_switches="-m 12000",loglevel="INFO",override=True)  # 12 GB memory

    main(mapdl)

    # Close Mechanical
    mapdl.exit()