#This Organizes the specified sub calls for each ANSYS build step
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
from ansys.mapdl.core import launch_mapdl
from ansys.dpf import core as dpf
import CGeometry
import CMesh
import CProperties
import CResults
import os
import pyvista as pv
from pathlib import Path
import shutil
import matplotlib.tri as mtri
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D

Nside = 5#Number of servos per side
Servo_width = 0.1#size of each servo area
DeviceWidth = 1
Cellwidth = DeviceWidth/Nside
thickness = 0.01
TotalModesToCalculate = 32
Resolution = 0.02

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
    return {label:''}
def ConstrainNodes(mapdl, label, x, y, Diam, Z_displacment, IncludeInner=True, plotme=False, FixedEdge=False):
    if IncludeInner:
        NodeDict = XYSquareSelect(mapdl, label, x, y, Diam)
    else:
        NodeDict = XYSquareSelect(mapdl, label, x, y, Diam, 0.025)

    mapdl.cmsel("s", label, 'NODE')
    if FixedEdge:
        mapdl.d('ALL', 'UX', 0)
        mapdl.d('ALL', 'UY', 0)
        mapdl.d('ALL', 'UZ', 0)
    else:
        mapdl.d('ALL', 'UZ', Z_displacment)
    this_nodelist = mapdl.mesh.nodes.copy()
    this_nodelist[:, 2] = Z_displacment

    if plotme:
        mapdl.nplot(vtk=True, show_node_numbering=True, color="green", point_size=10, background="w")
    return this_nodelist
def PlotNodeBC(mapdl,constrained_dict,ConstrainedNodes = np.nan):
    mapdl.allsel(mute=True)


    fig, ax = plt.subplots()
    mapdl.allsel(mute=True)
    coords = mapdl.mesh.nodes.copy()
    ax.scatter(coords[:, 0], coords[:, 1], color='lightgrey', s=10)
    print(constrained_dict)

    start = True
    for key, value in constrained_dict.items():
        mapdl.cmsel('s', key)
        coords = mapdl.mesh.nodes.copy()
        coords[:,2] = value*np.ones_like(coords[:, 2])
        if start:
            total_XYdisplacement_data = coords
            start = False
        else:
            total_XYdisplacement_data = np.vstack((total_XYdisplacement_data,coords))

    sc = ax.scatter(total_XYdisplacement_data[:, 0], total_XYdisplacement_data[:, 1], c=total_XYdisplacement_data[:, 2], cmap='turbo', s=10)

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
        servo_dict = {}
        #Build map from ServoIndex to xy
        corner_indices = [0, N - 1, N ** 2 - N, N ** 2 - 1]
        j = 0
        for i in range(N**2): #map the components
            #Check if in the corners
            if i not in corner_indices:

                row, col = divmod(i, N)
                x_center = col * Cellwidth + Cellwidth / 2 - DeviceWidth / 2
                y_center = row * Cellwidth + Cellwidth / 2 - DeviceWidth / 2
                label = f"ServoNodes_Group_{j}"
                servo_dict.update({label:ServoDisplacmentVect[j]})# Add to the server dict that maps componets
                print(f"Building:{label}, x,y [{x_center,y_center}],Z_disp:{ServoDisplacmentVect[j]}")
                NodeList_new = ConstrainNodes(mapdl,label,x_center,y_center,Servo_width,ServoDisplacmentVect[j], plotme=False)
                j = j + 1

        return servo_dict
    else:
        raise ValueError("ServoDisplacmentVect is of Incorrect length to map onto square")
def ManageFolders(folder_path):
    p = Path(folder_path)

    # Delete the folder and everything under it if it’s there
    if p.exists():
        shutil.rmtree(p)  # one call, nothing survives

    # Re‑create an empty folder
    p.mkdir(parents=True, exist_ok=True)
def RenderALL_ModalPics(rst,folder_path,**kwargs):
    ManageFolders(folder_path)
    print(f"Starting to Generate {rst.nsets} PNGS in {folder_path}")
    for i in range(rst.nsets):
        pv.close_all()
        image = rst.plot_nodal_displacement(i,
                                    show_displacement=True,
                                    displacement_factor=0.4,
                                    screenshot=f"{folder_path}/mode_{i}.png",
                                    add_text = f"Mode_{i}",
                                    **kwargs)
        #image.screenshot(f"{folder_path}/mode_{i}.png", window_size=(2048, 2048))
        #image.close()
    print(f"Finished Generating {rst.nsets} PNGS in {folder_path}")
def RenderALL_ModalGifs(rst,folder_path,**kwargs):
    ManageFolders(folder_path)
    print(f"Starting to Generate {rst.nsets} PNGS in {folder_path}")
    for i in range(rst.nsets):
        pv.close_all()
        rst.animate_nodal_displacement(i,
                                       displacement_factor=0.4,
                                       movie_filename=f"{folder_path}/Mode_{i}.gif",
                                       add_text = f"Mode_{i}",
                                       **kwargs)
    print(f"Finished Generating {rst.nsets} GIFS in {folder_path}")
def TransientAnalysis(mapdl):
    # kwargs = {
    #     "loop": True,
    #     "show_axes": False,
    #     "background": "w",
    #     "off_screen": False,
    # }
    # rst = mapdl.result  # make sure the .rst file was written
    # nsets = rst.nsets  # total sub‑steps in the file (integer)
    #
    # # build [(1,1), (1,2), …, (1,nsets)]
    # frames = [(1, i + 1) for i in range(nsets)]
    #
    # # sanity check
    # print(frames[:3], '...', frames[-1])  # should print [(1,1) ... (1,n)]
    #
    # # animate
    # rst.animate_nodal_solution(
    #     rnum=frames,  # REQUIRED in older versions
    #     comp='NORM',  # or 'X','Y','Z'
    #     movie_filename='transient.gif',
    #     scale_factor=0.02,  # warp = 2 % of part size
    #     show_edges=True,
    #     loop=True
    # )
    # print("Saved → transient.gif")

    rst_path = Path(mapdl.directory) / f"{mapdl.jobname}.rst"
    model = dpf.Model(str(rst_path))  # launches a DPF server

    mesh = model.metadata.meshed_region
    time = model.metadata.time_freq_support.time_frequencies.data  # (n_time,)

    # --- 2.  PULL THE FIELD(S) YOU CARE ABOUT --------
    u_fc = model.results.displacement().eval()  # FieldContainer, len = n_time
    # nodal L2 magnitude → stack into (n_time, n_nodes)
    u_mag = np.vstack([np.linalg.norm(f.data[:, :3], axis=1) for f in u_fc])

    coords = mesh.nodes.coordinates  # (n_nodes, 3)

    # --- 3.  QUICK PLOTS -----------------------------
    # scatter deformed shape at final time
    plt.figure()
    plt.scatter(coords[:, 0], coords[:, 1], c=u_mag[-1], s=4, cmap='turbo')
    plt.axis('equal');
    plt.colorbar(label='|u|  [m]')
    plt.title(f'|u| at t = {time[-1]:.4f} s')
    plt.show()

    # time trace of max displacement
    plt.figure()
    plt.plot(time, u_mag.max(1))
    plt.xlabel('t  [s]');
    plt.ylabel('max |u|  [m]')
    plt.title('Peak nodal displacement vs. time')
    plt.grid(True);
    plt.show()

    # --- 4.  (OPTIONAL) SAVE THE RAW DATA ------------
    np.savez_compressed('disp_data.npz',
                        time=time, u_mag=u_mag, coords=coords)
    print('saved → disp_data.npz  (reload in the same session or later)')
def main(mapdl):
    try:
        # Build plate Geometry wit specfied faces
        cellinfo,servo_area_ids = CGeometry.platebuilderV2(
            mapdl,
            DeviceWidth,
            Nside,
            Servo_width,
            Cellwidth,
            thickness=thickness,
            Resolution = Resolution,
            plot = False
        )

        constrained_nodes = []

        # Constrain outside
        OuterNodeList = ConstrainNodes(mapdl, 'Outside', 0, 0, DeviceWidth, 0, IncludeInner=False, plotme=False,FixedEdge=True)

        mapdl.cmsel('s', 'Outside')
        OuterNodeList = mapdl.mesh.nodes.copy()

        ServoDisplacmentVect = np.random.uniform(-1, 1, size=Nside**2-4)
        print(ServoDisplacmentVect)
        servo_dict = ConstrainByServo(ServoDisplacmentVect,Cellwidth,Servo_width,DeviceWidth)
        start = True
        for key,value in servo_dict.items():
            if start:
                mapdl.nsel("NONE")
                mapdl.cmsel('s', key)
                start = False
            else:
                mapdl.cmsel('A', key)
        ServoNodeList = mapdl.mesh.nodes.copy()
        ConstrainedNodes = np.vstack((OuterNodeList, ServoNodeList))
        constrained_dict = servo_dict.copy()
        constrained_dict.update({'Outside':0})
        print(constrained_dict)
        if False:
            PlotNodeBC(mapdl,constrained_dict,ConstrainedNodes=ConstrainedNodes)
        # solve1
        mapdl.allsel(mute=True)

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

        Static_Results = mapdl.post_processing
        if False:
            Static_Results.plot_nodal_displacement(
                'Z',
                show_displacement=True,
                smooth_shading=True,
            )
        mapdl.save()

        #Start of Modal
        mapdl.prep7()

        #Remove Servo constriants for modal
        start = True
        for key,value in servo_dict.items():
            mapdl.cmsel('s', key)
            mapdl.ddele('ALL', 'ALL')
            mapdl.d('ALL', 'UZ', '', key)
        mapdl.allsel()

        mapdl.slashsolu()  # = /SOLU
        mapdl.antype("MODAL")  # modal analysis
        mapdl.modopt("LANB", TotalModesToCalculate)  # Lanczos, keep 40 modes (pick your own number)
        mapdl.mxpand(TotalModesToCalculate, 0, 0, "YES")  # writes the mode-shape tables for MSUP later
        mapdl.solve()
        mapdl.finish(mute=True)

        rst = mapdl.result
        print(f"{rst.nsets} modes where found")  # number of mode shapes

        kwargs = {
            "show_axes": False,
            "background": "w",
            "off_screen": True,
            "n_colors": 10,
        }
        if False:
            RenderALL_ModalPics(rst,"Modal_Images",**kwargs)

        kwargs = {
            "loop":True,
            "n_frames":100,
            "show_axes":False,
            "background":"w",
            "off_screen":True,
        }
        if False:
            RenderALL_ModalGifs(rst, "Modal_gifs", **kwargs)

        #compare to zernike

        if True:
            # ---------- transient‑modal setup ----------
            # First Actuation
            Xi = np.random.uniform(-1, 1, size=Nside ** 2 - 4)
            print(f"Inital actuator position is {Xi}")
            # Second actuation
            Xf = np.random.uniform(-1, 1, size=Nside ** 2 - 4)
            print(f"Finial actuator position is {Xf}")

            mapdl.slashsolu()
            mapdl.antype('TRANS')
            mapdl.trnopt('MSUP')

            # ---- time stepping ----
            t_end = 0.5  # seconds  (end of this load step)
            dt = 1e-3  # initial sub‑step size
            t0, t1 = 0.0, 0.5
            mapdl.time(t_end)  # sets load‑step end time
            mapdl.deltim(dt)  # sets initial (and max) Δt

            mapdl.kbc(1)  # 1 = ramp table data

            # ---- damping & initial conditions ----
            mapdl.mdamp('ALL', 0.02)  # 2 % modal damping
            mapdl.ic('ALL', 'ALL')  # zero initial modal coords

            # ---- apply servo tables ----
            for k, comp in enumerate(servo_dict):
                tbl = f"SERVO{k + 1}"  # table already built: (t0, xi) → (t1, xf)
                mapdl.cmsel('S', comp, 'NODE')
                mapdl.d('ALL', 'UZ', '', tbl)
                mapdl.allsel()

            # ---------- solve ----------
            mapdl.solve()
            mapdl.finish()

            # ------------------- in PyMAPDL -------------------
            frames = [(1, i + 1) for i in range(mapdl.result.nsets)]  # 1‑based tuples
            mapdl.result.animate_nodal_solution(
                rnum=mapdl.result.nsets-1, comp='Z',
                movie_filename='transient.gif',
                displacement_factor=10,
                )

        if False: #Run at your own risk (Generates two pose vectors and uses modal super position
            TransientAnalysis(mapdl)

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