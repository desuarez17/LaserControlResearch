from ansys.mapdl.core import LOG

LOG.setLevel("DEBUG")
LOG.log_to_file("mylog.log")

from ansys.mapdl.core import launch_mapdl

mapdl = launch_mapdl(loglevel="DEBUG")