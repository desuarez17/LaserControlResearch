#This Organizes the specified sub calls for each ANSYS build step
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from ansys.mapdl.core import launch_mapdl
import CGeometry
import CMesh
import CProperties
import CResults

Nside = 5#Number of servos per side
Servo_width = 0.1#size of each servo area
DeviceWidth = 1
Cellwidth = DeviceWidth/Nside
thickness = 0.01


def XYSquareSelect(mapdl, label, x, y, Diam, thickness=np.nan):
    mapdl.allsel(mute=True)
    mapdl.nsel("S", "LOC", "X", x - Diam / 2, x + Diam / 2)  # Select line
    mapdl.nsel("R", "LOC", "Y", y - Diam / 2, y + Diam / 2)
    mapdl.cm('outer_sq', 'NODE')
    if thickness != np.nan:
        mapdl.nsel("S", "LOC", "X", x - Diam / 2 + thickness, x + Diam / 2 - thickness)  # Select Inner area
        mapdl.nsel("R", "LOC", "Y", y - Diam / 2 + thickness, y + Diam / 2 - thickness)
        mapdl.cm('inner_sq', 'NODE')
        # Take diffrence of square areas
        mapdl.cmsel('S', 'outer_sq', 'NODE')
        mapdl.cmsel('U', 'inner_sq', 'NODE')

    mapdl.cm(label, "NODE")
    return label
def ConstrainNodes(mapdl, label, x, y, Diam, Z_displacment, IncludeInner=True, plotme=False, FixedEdge=False):
    if IncludeInner:
        XYSquareSelect(mapdl, label, x, y, Diam)
    else:
        XYSquareSelect(mapdl, label, x, y, Diam, 0.025)

    mapdl.cmsel("s", label, 'NODE')
    if FixedEdge:
        mapdl.d('ALL', 'UX', 0)
        mapdl.d('ALL', 'UY', 0)
    mapdl.d('ALL', 'UZ', Z_displacment)
    this_nodelist = mapdl.mesh.nodes.copy()
    this_nodelist[:, 2] = Z_displacment

    if plotme:
        mapdl.nplot(vtk=True, show_node_numbering=True, color="green", point_size=10, background="w")
    return this_nodelist
def PlotNodeBC(mapdl,ConstrainedNodes = np.nan):
    mapdl.allsel(mute=True)

    coords = mapdl.mesh.nodes.copy()

    # --- plot ---
    fig, ax = plt.subplots()

    # 1. Plot all nodes grey
    ax.scatter(coords[:, 0], coords[:, 1], color='lightgrey', s=10)

    sc = ax.scatter(ConstrainedNodes[:, 0], ConstrainedNodes[:, 1], c=ConstrainedNodes[:, 2], cmap='turbo', s=10)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Constraints Visualization')
    plt.axis('equal')
    plt.legend()
    plt.show()
def ConstrainByServo(ServoDisplacmentVect,Cellwidth,Servo_width,DeviceWidth):
    print(Cellwidth)
    #check if ServoDisplacmentVect is valid
    N = np.sqrt(ServoDisplacmentVect.size+4)
    print(f"WE got {N}, Is int:{N.is_integer()}")
    if N.is_integer():
        #We have good mapping
        N = int(N)

        #Build map from ServoIndex to xy
        corner_indices = [0, N - 1, N ** 2 - N, N ** 2 - 1]
        j = 0
        for i in range(N**2):
            #Check if in the corners
            if i not in corner_indices:

                row, col = divmod(i, N)
                x_center = col * Cellwidth + Cellwidth / 2 - DeviceWidth / 2
                y_center = row * Cellwidth + Cellwidth / 2 - DeviceWidth / 2
                label = f"ServoNodes_Group_{j}"
                print(f"Building x,y [{x_center,y_center}],Z_disp:{ServoDisplacmentVect[j]}")
                NodeList_new = ConstrainNodes(mapdl,label,x_center,y_center,Servo_width,ServoDisplacmentVect[j], plotme=False)
                # print(NodeList_new)
                print(NodeList_new.shape)
                if j == 0:
                    NodeList = NodeList_new
                else:
                    NodeList = np.vstack((NodeList, NodeList_new))
                j = j + 1

        return NodeList
    else:
        raise ValueError("ServoDisplacmentVect is of Incorrect length to map onto square")
def main(mapdl):
    try:

        # Build plate Geometry wit specfied faces
        cellinfo,servo_area_ids = CGeometry.platebuilderV2(mapdl,DeviceWidth,Nside,Servo_width,Cellwidth,thickness=thickness)

        constrained_nodes = []

        # Constrain outside
        OuterNodeList = ConstrainNodes(mapdl, 'Outside', 0, 0, DeviceWidth, 0, IncludeInner=False, plotme=False,FixedEdge=True)

        ServoDisplacmentVect = np.random.uniform(-1, 1, size=Nside**2-4)
        # ServoNodeList = ConstrainNodes(mapdl, 'InnerPoint', 0.25, 0.25, Servo_width, 0.4, IncludeInner=True, plotme=True)
        print(ServoDisplacmentVect)

        ServoNodeList = ConstrainByServo(ServoDisplacmentVect,Cellwidth,Servo_width,DeviceWidth)

        ConstrainedNodes = np.vstack((OuterNodeList, ServoNodeList))

        PlotNodeBC(mapdl,ConstrainedNodes=ConstrainedNodes)
        # solve1
        mapdl.allsel(mute=True)


        #Matplot Constrains


        # Solve the Static Problem
        # ~~~~~~~~~~~~~~~~~~~~~~~~
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
        # mapdl.plnsol('UZ')
        mapdl.post_processing.plot_nodal_displacement('Z',show_node_numbering=False)
        #Show max Stress
        result = mapdl.result
        result.plot_element_displacement(
            "Z",
            smooth_shading = True,
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
    mapdl = launch_mapdl(run_location=r"C:\Users\damia\OneDrive\Desktop\drive\School Vault\RIT\Research\Ansys\MAPDL_FILES", additional_switches="-m 12000",loglevel="error",override=True)  # 12 GB memory

    main(mapdl)

    # Close Mechanical
    mapdl.exit()