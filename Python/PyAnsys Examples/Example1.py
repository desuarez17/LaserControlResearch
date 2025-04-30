from ansys.mapdl.core import launch_mapdl

jobName = "Example1_2"  # optional
mapdl = launch_mapdl(jobname=jobName)

#making Geometry
box1 = [0, 6, -1, 1] #x1,x2,y1,y2
box2 = [4, 6, -1, -3]

#Prep Geometry builder
mapdl.prep7()

# build your cubes
mapdl.rectng(box1[0], box1[1], box1[2], box1[3])
mapdl.rectng(*box2)  # Same as above with Kwargs

# Create first circle
radius = 1
circle1_X = box1[0]
circle1_Y = (box1[2] + box1[3]) / 2
mapdl.cyl4(circle1_X, circle1_Y, radius)

circle2_X = (box2[0] + box2[1]) / 2
circle2_Y = box2[3]
mapdl.cyl4(circle2_X, circle2_Y, radius)

#Group all the solids into 1 area
mapdl.aadd("all")

#make filet
line1 = mapdl.lsel("S", "LOC", "Y", box1[2])
l1 = mapdl.get("line1", "LINE", 0, "NUM", "MAX")
line2 = mapdl.lsel("S", "LOC", "X", box2[0])
l2 = mapdl.get("line2", "LINE", 0, "NUM", "MAX")

fillet_radius = 0.4
mapdl.allsel()
line3 = mapdl.lfillt("line1", l2, fillet_radius)

mapdl.allsel()


#Create fillet area
mapdl.allsel()

# Select lines for the area
mapdl.lsel("S", "LENGTH", "", fillet_radius)

#Remove the fillet line trang
mapdl.lsel("A", "LINE", "", line3)

# Create the area
mapdl.al("ALL")  # Prints the ID of the newly created area
# Add the area to the main area
mapdl.aadd("all")


# Create the first pinhole
pinhole_radius = 0.4
pinhole1_X = box1[0]
pinhole1_Y = (box1[2] + box1[3]) / 2

pinhole1 = mapdl.cyl4(pinhole1_X, pinhole1_Y, pinhole_radius)
pinhole2_X = (box2[0] + box2[1]) / 2
pinhole2_Y = box2[3]

pinhole2 = mapdl.cyl4(pinhole2_X, pinhole2_Y, pinhole_radius)
pinhole2_lines = mapdl.asll("S", 0)
# Remove pin hole areas from bracket
mapdl.asba("all", pinhole1)
bracket = mapdl.asba("all", pinhole2)
mapdl.aplot(vtk=True, show_lines=True, cpos="xy")

#MATERIAL PROP
ex = 30e6  # Young's Modulus
prxy = 0.27  # Poisson's ratio
mapdl.mp("EX", 1, ex)
mapdl.mp("PRXY", 1, prxy)

#PLANE THICK
# define a ``PLANE183`` element type with thickness
mapdl.et(1, "PLANE183", kop3=3)
thick = 0.5
mapdl.r(1, thick)  # thickness of 0.5 length units)


#MESH TIME
element_size = 0.5
mapdl.esize(element_size)
mapdl.amesh(bracket)
mapdl.eplot(
    vtk=True,
    cpos="xy",
    show_edges=True,
    show_axes=False,
    line_width=2,
    background="w",
)

#BC
mapdl.allsel()
mapdl.solution()
mapdl.antype("STATIC")