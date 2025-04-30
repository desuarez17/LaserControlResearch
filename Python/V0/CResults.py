# Post-Processing
# ~~~~~~~~~~~~~~~
# The static result can be post-processed both within MAPDL and
# outside of MAPDL using ``pyansys``.  This example shows how to
# extract the von Mises stress and plot it using the ``pyansys``
# result reader.
import numpy as np

def max_stress(mapdl):
    print("Displaying Max_VonMises_Stress")

    # grab the result from the ``mapdl`` instance
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

    nnum, stress = result.principal_nodal_stress(0)
    von_mises = stress[:, -1]  # von-Mises stress is the right most column

    # Must use nanmax as stress is not computed at mid-side nodes
    max_stress = np.nanmax(von_mises)