from matplotlib import pyplot as plt
import numpy as np

def platebuilder(mapdl,DeviceWidth,Nside,Servo_width,Cellwidth,thickness=1):
    print("Begining Geometry Builder")

    # Start GeoBuild
    mapdl.prep7()

    mapdl.blc5(0,0,width=DeviceWidth, height=DeviceWidth)#main area

    mapdl.get("base_id", "AREA", 0, "NUM", "MAX") #Get plate main ID
    base_id = int(mapdl.parameters["base_id"])

    # Dictionary to track origins and area indices
    cellinfo = {}
    servo_area_ids = []

    corner_indices = [0, Nside - 1, Nside ** 2 - Nside, Nside ** 2 - 1]
    # Start area indexing from 2 (assuming area 1 is the main block)
    for i in range(Nside**2):
        #Check if in the corners
        if i not in corner_indices:
            row, col = divmod(i, Nside)

            x_center = col * Cellwidth + Cellwidth / 2 - DeviceWidth / 2
            y_center = row * Cellwidth + Cellwidth / 2 - DeviceWidth / 2

            mapdl.blc5(x_center, y_center, width=Servo_width, height=Servo_width)

            mapdl.get("temp_area_id", "AREA", 0, "NUM", "MAX")
            area_id = int(mapdl.parameters["temp_area_id"])

            # Select this area's lines
            mapdl.asel("S", "AREA", "", area_id)
            mapdl.lsla("S")
            mapdl.lesize("ALL", Servo_width / 2, kforc=1)

            cellinfo[area_id] = [x_center, y_center, Servo_width]
            servo_area_ids.append(area_id)

    #print(cellinfo)

    # Show Vetex plot
    # mapdl.lsla("S")
    # mapdl.lplot(vtk=True, show_keypoint_numbering=True)
    # mapdl.lsel("all")

    # plot the area using vtk/pyvista
    # mapdl.aplot(vtk=True, show_area_numbering=True, show_lines=True, cpos="xy")

    # for cell_id in servo_area_ids:
    #     mapdl.asba(base_id, cell_id)  # Area subtract to split face into subregions
    #mapdl.asba(base_id,2)
    # mapdl.asba(base_id, servo_area_ids)
    #extrude the area to create volume

    # Create areas (already done)
    mapdl.asel("ALL")  # Make sure all areas are selected
    mapdl.vext("ALL", dz=thickness)  # Extrude all areas into volumes

    # Checking volume plot
    #mapdl.vplot(vtk=True, show_lines=True, show_axes=True, smooth_shading=True)

    return cellinfo,servo_area_ids
def platebuilderV2(mapdl,DeviceWidth,Nside,Servo_width,Cellwidth,thickness=1):
    print("Begining Geometry Builder")

    # Start GeoBuild
    mapdl.prep7()

    mapdl.blc5(0, 0, width=DeviceWidth, height=DeviceWidth, depth=thickness)  # main area
    mapdl.et(1, "SOLID186")

    mapdl.mshkey(0)
    mapdl.mshape(1, "3D")
    # mapdl.SMRT(6)
    mapdl.vsweep("all")
    mapdl.eplot(vtk=True, show_edges=True, show_axes=False, line_width=2, background="w")

    # Dictionary to track origins and area indices
    cellinfo = {}
    servo_area_ids = []

    return cellinfo,servo_area_ids