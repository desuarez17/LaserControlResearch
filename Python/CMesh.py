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

def platemesh(mapdl,servo_area_ids,thickness=1):
    print("Begining Mesher")

    # # Mesh the volume
    # mapdl.esize(0.01)  # Set global mesh size
    # for area_id in servo_area_ids:
    #     mapdl.lesize(area_id, size=0.005)  # Finer mesh for servo areas
    mapdl.et(1, 186)

    mapdl.mshkey(1)
    mapdl.mshape(0, "3D")
    mapdl.vsweep("ALL")
    mapdl.eplot(vtk=True, show_edges=True, show_axes=False, line_width=2, background="w")