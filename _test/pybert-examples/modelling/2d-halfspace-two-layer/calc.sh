#!/usr/bin/env bash

# Create a path for meshing stuff
mkdir -p mesh

# To spare some typing we define a variable for the resulting mesh
MESH=mesh/world

# For the 2d meshing in this example we apply the Triangle (http://www.cs.cmu.edu/~quake/triangle.html)
# The meshing procedure is similar to 3d-halfspace-homogeneous example.
# First we create a PLC and then we let Triangle build the mesh.
# We start with a 2 dimensional simulation world with a bounding box [-100,-50] [100,0] and region marker 1.
# Please note, for some unknown reasons lies the region marker in the UPPER maximum bounding box corner. (to the opposite on 3D worlds)
# We will fix this some day when we rewrite the poly tools using python.
polyCreateWorld -d2 -x200 -z50 -m1 $MESH
# -d 2 world be 2 dimensional

# The geometry of the heterogeneity (the interface between the layers) need to be added manually due to the lack of suitable poly tools.
# The interface is a simple horizontal line starts from left boundary to right boundary at 1m depth.
# We define the interface via coordinate points that will be linear connected.
# The interface can be complex but every coordinate must lie inside the world.
# Write all coordinates into file mesh/layer1.txt and let a polyAddProfile add them into the world.
# Possible intersections will be considered automatic but you should ensure that every resulting region will get his own region marker.
echo "-100 -1" > mesh/layer1.xy
echo "100 -1" >> mesh/layer1.xy
polyAddProfile -i mesh/layer1.xy $MESH
# -i add file with interface coordinates

# Now define the lower layer (the background) as region with marker 2. Add the appropriate marker below the interface at [0.0, 0.0, -1.05]
polyAddVIP -z -1.05 -R -m2 $MESH
# -R VIP is a region marker
# -m 2 region get the marker 2

# Now we need to add 24 electrodes from [0.0, 0.0, 0.0] to [23.0 0.0, 0.0]
polyAddProfile -x0.0 -n 24 -X23.0 -m -99 $MESH
# -x,y,z start coordinate
# -X,Y,Z end coordinate
# -n 24 24 electrodes between start and end
# -m 99 VIP will get marker -99 and so becomes electrodes
# view poly in paraview

# Electrodes need to be locally refined
polyRefineVIPS -z -0.1 $MESH

# We can convert the PLC into VTK for a visual feedback
# TODO 2D poly should be also read by pytripatch
polyConvert -V -o $MESH'Poly' $MESH

# Every unstructured mesh needs a quality criteria to be meet.
# Triangle tries to achieve a minimum angle quality criteria.
# You should carefully choose this quality value between 30 and 34.4.
# Larger values tend to meshes with to small triangles that waste calculation resources.
QUALITY=34.0

# Now we can create the mesh with the desired quality. We wrap the Triangle library for an easier handling.
# Additionally we can apply a simple smoothing of the resulting mesh that results in some kind of nicer mesh.
dctriangle -v -q $QUALITY -S $MESH
# -v be verbose
# -q desired mesh quality
# -S smooth the mesh
# $MESH should be $MESH.poly and results ind $MESH.bms

# The resulting mesh can be converted into a vtk to be viewed in Paraview or can be visualized with pytripatch.
# Maybe you need to zoom and move the mesh a bit to see all features.
# Green boundary denote earth subsurface and homogeneous Neumann boundary condition, red line denote mixed or Robyn boundary condition for the subsurface boundary.
pytripatch -e mesh -d marker -E --label='Region marker' $MESH.bms &
# -e show electrode and use coordinates from the mesh itself
# -d data show the current region marker
# -E show all triangle edges
# --label set the color bar label

# To map the region marker to the desired resistivity values we have to create a rho.map file.
# Here we map all cells with the region marker 1 to 10 Ohmm and all with region 2 to 100 Ohmm.
echo "1 10"  > rho.map
echo "2 100" >> rho.map

# We delegate this mapping file to dcmod and calculate our modeling response.
dcmod -v -a rho.map -s wa24.shm $MESH.bms
# -a add rho map

# Finally we can convert the impedances into apparent resistivities.
# If this file is considered to an inversion we NEED to add some normal contributed noise to fit requirements for the basic inversion theory.
dcedit -v -E -e3 -N -o wa24.dat wa24.ohm -f 'a b m n rhoa err'
# -E estimate data error based on error level and measured voltage
# -e error level 1$
# -N add some normal distributed noise based on estimated error level

# The resulting data can be viewed as pseudosection with pyshowdata.py.
# Please note that pyshowdata need some further improvements but give at least some first impressions.
pyshowdata.py wa24.dat






