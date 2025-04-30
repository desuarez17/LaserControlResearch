from ansys.mapdl.core import launch_mapdl

# Launch MAPDL
mapdl = launch_mapdl(run_location=r"C:\Users\damia\OneDrive\Desktop\drive\School Vault\RIT\Research\Ansys\MAPDL_FILES",
                     additional_switches="-m 12000", loglevel="error", override=True)

# Create a simple model (example)
mapdl.prep7()
mapdl.block(0, 10, 0, 10, 0, 10)
mapdl.et(1, 186)
mapdl.vmesh('all')

# Create a node component named 'my_component' (example)
mapdl.nsel('S', 'LOC', 'X', 0)
mapdl.cm('my_component', 'NODE')
mapdl.allsel()

# Select the nodes of the component
mapdl.cmsel('s', 'my_component')

# Get the node numbers of the selected nodes
component_nodes = mapdl.mesh.nnum

# Print the node numbers
print(component_nodes)

# Exit MAPDL
mapdl.exit()