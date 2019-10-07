#!/usr/bin/env bash

mkdir -p mesh

# The creation of a modeling mesh consists always on 2 Steps.
# The first step is to define the mesh geometry and the 2nd step is to let the mesh generator create a mesh out of this geometry definition.
# In this example we use TetGen (http://wias-berlin.de/software/tetgen/) for doing the meshing job so we are constrained to the TetGen geometry definition standard called the Piecewise Linear Complexes (PLC).
# The PLC is collection of nodes and facets that define the shape of the meshing regions.
#
# First we need a main modeling domain what we call 'world'.
# A simple world is a cube with specialized boundary markers for an air interface (the earths surface at the top z==0) 
# and 5 interior boundaries.
#
# We start with polyCreateWorld to create a world with the dimensions x=1000m, y=1000m and a depth of 500m.
# The origin is in the center of the top surface, so the bounding box of out world is [-500,-500,-500] -- [500,500,0]
# In the finished mesh we need to identify which mesh cells are part of which mesh region so we distribute region marker.
# Our world becomes region no. 1 with -m1. 
# Every Region of the PLC need one marker on arbitrary position inside the region. 
# The default world region marker lies beside the lower corner of the maximum bounding box. 
polyCreateWorld -x1000 -y1000 -z500 -m1 mesh/world
# -x x-coordinate
# -y x-coordinate
# -z x-coordinate
# -m marker for the node
# mesh/world PLC to be processed

# A new file mesh/world.poly has been created that contains the world PLC
# You can convert every PLC file into the vtk file format to take a look with paraview (http://www.paraview.org/)
polyConvert -V -o mesh/worldPLC mesh/world
# -V write vtk-format
# -o output filname mesh/worldPLC.vtk (.vtk will be added automatic)
# mesh/world PLC to be meshed mesh/world

# Usually we need electrode positions inside the mesh to perform a suitable simulation.
# We now put four free nodes at (0,0,0),(1,0,0), (10,0,0) and (11,0,0) into the PLC of our world and denote them to be electrodes by marking them with -99
polyAddVIP -x0 -y0 -z0 -m -99 mesh/world
polyAddVIP -x1 -y0 -z0 -m -99 mesh/world
polyAddVIP -x10 -y0 -z0 -m -99 mesh/world
polyAddVIP -x11 -y0 -z0 -m -99 mesh/world
# -x x-coordinate
# -y x-coordinate
# -z x-coordinate
# -m marker for the node
# mesh/world PLC to be processed

# The current injection via the Point Electrode Model (PEM) at an electrode node leads to large numerical inaccuracies due to a discretization error for the singular current density. 
# We found a local mesh refinement in the vicinity of the electrode nodes reduces this discretization error to an degree that is suitable for geophysicists needs.
# We force the mesh to be refined in vicinity of the electrodes by giving them a new free node below the electrodes at 1/10 (-z -0.1) electrode spacing (Ruecker et al., 2006)
polyRefineVIPS -z -0.1 mesh/world
# -z refinement direction
# mesh/world PLC to be processed

# Our PLC contains now a big cube and four nodes, this goes into TetGen
tetgen -pazQAq1.12 mesh/world
# -p PLC input format (needed)
# -a area infos (needed)
# -z call from 1 (needed)
# -Q be Quiet (optinal)
# -A assing attributes (needed)
# -q mesh quality (needed)
# mesh/world PLC to be meshed mesh/world

# Since the TetGen output will be called mesh/world.1.node/.ele/.face we convert it to our mesh format (.bms) using meshconvert.
# By the way we make a global refinement using the -p switch (quadratic shape functions).
meshconvert -v -iT -BD -V -o mesh/world mesh/world.1
# -v be verbose, 
# -iT input tetgen format
# -BD binary dcfemlib output format
# -V additional vtk output to view the mesh in paraview
# -p p-refine the mesh (-p for 3D@bert1 is broken and will not be fixed.)
# we use a python call instead
python -c 'import pygimli as pg; m=pg.load("mesh/world.bms"); m=m.createP2(); m.save("mesh/world.bms");'

# -o output filename = mesh/world (.bms will be added automatic)
# mesh/world.1  name of the input mesh

# We can now remove temporary stuff. 
rm -rf mesh/world.1*

# The resulting mesh for the simulation called mesh/world.bms
