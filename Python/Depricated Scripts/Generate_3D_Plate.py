
from matplotlib import pyplot as plt

# sphinx_gallery_thumbnail_number = 3
import numpy as np

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(loglevel="ERROR")

# Geometry
###############################################################################

length = 0.4
width = 0.1

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
mapdl.lsel("all")


# Next, extrude the area to create volume
thickness = 0.01
mapdl.vext(cut_area, dz=thickness)

# Checking volume plot
mapdl.vplot(vtk=True, show_lines=True, show_axes=True, smooth_shading=True)





###############################################################################
# Batch Analysis
# ~~~~~~~~~~~~~~
# The above script can be placed within a function to compute the
# stress concentration for a variety of hole diameters.  For each
# batch, MAPDL is reset and the geometry is generated from scratch.
#
# .. note::
#    This section has been disabled to reduce the execution time of
#    this example. Enable it by setting ``RUN_BATCH = TRUE``

RUN_BATCH = False


def compute_stress_con(ratio):
    notch_depth = ratio * width / 2

    mapdl.clear()
    mapdl.prep7()

    # Notch circle.
    circ0_kp = mapdl.k(x=length / 2, y=width + notch_radius)
    circ_line_num = mapdl.circle(circ0_kp, notch_radius)
    circ_line_num = circ_line_num[2:]  # only concerned with the bottom arcs

    circ0_kp = mapdl.k(x=0, y=0)
    k1 = mapdl.k(x=0, y=-notch_depth)
    l0 = mapdl.l(circ0_kp, k1)
    mapdl.adrag(*circ_line_num, nlp1=l0)

    circ1_kp = mapdl.k(x=length / 2, y=-notch_radius)
    circ_line_num = mapdl.circle(circ1_kp, notch_radius)
    circ_line_num = circ_line_num[:2]  # only concerned with the top arcs

    k0 = mapdl.k(x=0, y=0)
    k1 = mapdl.k(x=0, y=notch_depth)
    l0 = mapdl.l(k0, k1)
    mapdl.adrag(*circ_line_num, nlp1=l0)

    rect_anum = mapdl.blc4(width=length, height=width)
    cut_area = mapdl.asba(rect_anum, "ALL")  # cut all areas except the plate

    mapdl.allsel()
    mapdl.vext(cut_area, dz=thickness)

    notch_esize = np.pi * notch_radius * 2 / 50
    plate_esize = 0.01

    mapdl.asel("S", "AREA", vmin=1, vmax=1)

    mapdl.lsel("NONE")
    for line in [7, 8, 20, 21]:
        mapdl.lsel("A", "LINE", vmin=line, vmax=line)

    mapdl.ksel("NONE")
    mapdl.ksel(
        "S",
        "LOC",
        "X",
        length / 2 - notch_radius * 1.1,
        length / 2 + notch_radius * 1.1,
    )
    mapdl.lslk("S", 1)
    mapdl.lesize("ALL", notch_esize, kforc=1)
    mapdl.lsel("ALL")

    mapdl.mopt("EXPND", 0.7)  # default 1

    esize = notch_esize * 5
    if esize > thickness / 2:
        esize = thickness / 2  # minimum of two elements through

    mapdl.esize()  # this is tough to automate
    mapdl.et(1, "SOLID186")
    mapdl.vsweep("all")

    mapdl.allsel()

    # Uncomment if you want to print geometry and mesh plots.
    # mapdl.vplot(savefig=f'vplot-{ratio}.png', off_screen=True)
    # mapdl.eplot(savefig=f'eplot-{ratio}.png', off_screen=True)

    mapdl.units("SI")  # SI - International system (m, kg, s, K).

    mapdl.mp("EX", 1, 210e9)  # Elastic moduli in Pa (kg/(m*s**2))
    mapdl.mp("DENS", 1, 7800)  # Density in kg/m3
    mapdl.mp("NUXY", 1, 0.3)  # Poisson's Ratio

    mapdl.nsel("S", "LOC", "X", 0)
    mapdl.d("ALL", "UX")

    mapdl.nsel("R", "LOC", "Y", width / 2)
    mapdl.d("ALL", "UY")
    mapdl.d("ALL", "UZ")

    mapdl.nsel("S", "LOC", "X", length)
    mapdl.cp(5, "UX", "ALL")

    mapdl.nsel("R", "LOC", "Y", width / 2)  # selects more than one
    single_node = mapdl.mesh.nnum[0]
    mapdl.nsel("S", "NODE", vmin=single_node, vmax=single_node)
    mapdl.f("ALL", "FX", 1000)

    mapdl.allsel(mute=True)

    mapdl.run("/SOLU")
    mapdl.antype("STATIC")
    mapdl.solve()
    mapdl.finish()

    result = mapdl.result
    _, stress = result.principal_nodal_stress(0)
    von_mises = stress[:, -1]  # von-Mises stress is the right most column
    max_stress = np.nanmax(von_mises)

    mask = result.mesh.nodes[:, 0] == length
    far_field_stress = np.nanmean(von_mises[mask])

    adj = width / (width - notch_depth * 2)
    stress_adj = far_field_stress * adj

    return max_stress / stress_adj


###############################################################################
# Run the batch and record the stress concentration

if RUN_BATCH:
    k_t_exp = []
    ratios = np.linspace(0.05, 0.75, 9)
    print("    Ratio  : Stress Concentration (K_t)")
    for ratio in ratios:
        stress_con = compute_stress_con(ratio)
        print("%10.4f : %10.4f" % (ratio, stress_con))
        k_t_exp.append(stress_con)

def calc_teor_notch(ratio):
    notch_depth = ratio * width / 2
    h = notch_depth
    r = notch_radius
    D = width

    if 0.1 <= h / r <= 2.0:
        c1 = 0.85 + 2.628 * (h / r) ** 0.5 - 0.413 * h / r
        c2 = -1.119 - 4.826 * (h / r) ** 0.5 + 2.575 * h / r
        c3 = 3.563 - 0.514 * (h / r) ** 0.5 - 2.402 * h / r
        c4 = -2.294 + 2.713 * (h / r) ** 0.5 + 0.240 * h / r
    elif 2.0 <= h / r <= 50.0:
        c1 = 0.833 + 2.069 * (h / r) ** 0.5 - 0.009 * h / r
        c2 = 2.732 - 4.157 * (h / r) ** 0.5 + 0.176 * h / r
        c3 = -8.859 + 5.327 * (h / r) ** 0.5 - 0.32 * h / r
        c4 = 6.294 - 3.239 * (h / r) ** 0.5 + 0.154 * h / r

    return c1 + c2 * (2 * h / D) + c3 * (2 * h / D) ** 2 + c4 * (2 * h / D) ** 3


###############################################################################
# which is used later to calculate the concentration factor for the given ratios:

if RUN_BATCH:
    print("    Ratio  : Stress Concentration (K_t)")
    k_t_anl = []
    for ratio in ratios:
        stress_con = calc_teor_notch(ratio)
        print("%10.4f : %10.4f" % (ratio, stress_con))
        k_t_anl.append(stress_con)


###############################################################################
# Analytical Comparison
# ~~~~~~~~~~~~~~~~~~~~~
#
# As shown in the following plot, MAPDL matches the known tabular
# result for this geometry remarkably well using PLANE183 elements.
# The fit to the results may vary depending on the ratio between the
# height and width of the plate.

if RUN_BATCH:
    plt.plot(ratios, k_t_anl, label=r"$K_t$ Analytical")
    plt.plot(ratios, k_t_exp, label=r"$K_t$ ANSYS")
    plt.legend()
    plt.show()

###############################################################################
# Stop mapdl
# ~~~~~~~~~~
#
mapdl.exit()
