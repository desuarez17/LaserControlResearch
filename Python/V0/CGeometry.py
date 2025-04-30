from matplotlib import pyplot as plt
import numpy as np

def platebuilder(mapdl,thickness=1,width=0.4,length=0.1):
    print("Begining Geometry Builder")

    notch_depth = 0.04
    notch_radius = 0.01

    # create the half arcs
    mapdl.prep7()

    circ0_kp = mapdl.k(x=length / 2, y=width + notch_radius)
    circ_line_num = mapdl.circle(circ0_kp, notch_radius)
    circ_line_num = circ_line_num[2:]  # only concerned with the bottom arcs

    # create a line and drag the top circle downward
    circ0_kp = mapdl.k(x=0, y=0)
    k1 = mapdl.k(x=0, y=-notch_depth)
    l0 = mapdl.l(circ0_kp, k1)
    mapdl.adrag(*circ_line_num, nlp1=l0)

    # same thing for the bottom notch (except upwards
    circ1_kp = mapdl.k(x=length / 2, y=-notch_radius)
    circ_line_num = mapdl.circle(circ1_kp, notch_radius)
    circ_line_num = circ_line_num[:2]  # only concerned with the top arcs

    # create a line whereby the top circle will be dragged up
    k0 = mapdl.k(x=0, y=0)
    k1 = mapdl.k(x=0, y=notch_depth)
    l0 = mapdl.l(k0, k1)
    mapdl.adrag(*circ_line_num, nlp1=l0)

    rect_anum = mapdl.blc4(width=length, height=width)

    # Note how pyansys parses the output and returns the area numbers
    # created by each command.  This can be used to execute a boolean
    # operation on these areas to cut the circle out of the rectangle.
    # plate_with_hole_anum = mapdl.asba(rect_anum, circ_anum)
    cut_area = mapdl.asba(rect_anum, "ALL")  # cut all areas except the plate


    mapdl.lsla("S")
    mapdl.lplot(vtk=True, show_keypoint_numbering=True)
    mapdl.lsel("all")

    # plot the area using vtk/pyvista
    mapdl.aplot(vtk=True, show_area_numbering=True, show_lines=True, cpos="xy")

    # Next, extrude the area to create volume
    mapdl.vext(cut_area, dz=thickness)

    # Checking volume plot
    mapdl.vplot(vtk=True, show_lines=True, show_axes=True, smooth_shading=True)


