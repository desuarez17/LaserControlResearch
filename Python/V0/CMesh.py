###############################################################################
# Meshing
# ~~~~~~~
# This example will use PLANE183 elements as a thin plate can be
# modeled with plane elements provided that KEYOPTION 3 is set to 3
# and a thickness is provided.
#
# Mesh the plate using a higher density near the hole and a lower
# density for the remainder of the plate by setting ``LESIZE`` for the
# lines nearby the hole and ``ESIZE`` for the mesh global size.
#
# Line numbers can be identified through inspection using ``lplot``

# define a PLANE183 element type with thickness
import numpy as np

def platemesh(mapdl,notch_radius,thickness=1):
    print("Begining Mesher")
    # ensure there are at 25 elements around the hole
    notch_esize = np.pi * notch_radius * 2 / 50
    plate_esize = 0.01

    # increased the density of the mesh at the notch
    # line and area numbers identified using aplot

    mapdl.asel("S", "AREA", vmin=1, vmax=1)
    mapdl.aplot(vtk=True, show_line_numbering=True)


    mapdl.lsel("NONE")
    for line in [7, 8, 20, 21]:
        mapdl.lsel("A", "LINE", vmin=line, vmax=line)
    mapdl.lesize("ALL", notch_esize, kforc=1)
    mapdl.lsel("ALL")

    # Decrease the area mesh expansion.  This ensures that the mesh
    # remains fine nearby the hole
    mapdl.mopt("EXPND", 0.7)  # default 1

    # mesh several elements through the plate
    esize = notch_esize * 5
    if esize > thickness / 2:
        esize = thickness / 2  # minimum of two elements through

    mapdl.esize()  # this is tough to automate
    mapdl.et(1, "SOLID186")
    mapdl.vsweep("all")
    mapdl.eplot(vtk=True, show_edges=True, show_axes=False, line_width=2, background="w")