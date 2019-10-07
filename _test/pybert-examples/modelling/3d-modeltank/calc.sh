#!/usr/bin/env bash

# Create a path for the meshing stuff
mkdir -p mesh

# Defines how the PLC (*.poly) and the mesh (*.bms/vtk) will be called
MESH=mesh/tank

# Create the PLC for the modelling tank
bash tankPLC.sh $MESH

# Convert poly file into a vtk file for paraview
# Hint: use Display->Style: Wireframe and/or create glyphs(spheres) to see the electrodes)
polyConvert -V -o$MESH'PLC' $MESH

# Call TetGen to create mesh (*.1.*).
# TetGen also needs a quality criteria. 
# See TetGen manual for further details. (http://wias-berlin.de/software/tetgen/)
# Values between 1.2 and 1.12 are mostly sufficient.
tetgen -pazVAC -q1.2 $MESH 

# Convert the mesh *.1.* into *.bms (for calculation) and *.vtk (for paraview).
meshconvert -vDBT -iT -o $MESH $MESH.1
# Deletes the temporary TetGen mesh.
rm $MESH.1.* 

# Perform finite element simulation. 
# Note: -o overwrites default name settings modeltank.shm/.ohm.
dcmod -v -s modeltank.shm -o homogeneous $MESH

# Results are in homogeneous.ohm/homogeneous.collect and contain the simulated impedances which are the reciprocity values of the geometric factor.

# Alternatively we can do the same with a quadratic mesh (meshconvert -p) and using a coarser refinement (-q increased value).
# Which is more accurate or faster at a certain accuracy?

################################################################################
# PART 2: Inhomogeneous model
################################################################################

# We create an inhomogeneity and merge it with the above PLC:
# Create a hexagonal PLC with marker 2 and the bounding Box[0.55, 0.1, -0.4][0.85, 0.3, 0.4]
polyCreateCube -m 2 mesh/cube
polyScale -x 0.3 -y 0.2 -z 0.8 mesh/cube 
polyTranslate -x 0.7 -y 0.2 mesh/cube

# Merge this heterogeneity into the modelling tank. 
# polyMerge tries to recognize if the PLC are touching each other which should be no problem. 
# polyMerge will not generate a valid PLC if both sub domains are intersecting.
polyMerge $MESH mesh/cube $MESH'Inhomogen'
# polyMerge first-PLC second-PLC result-PLC

# Convert poly file for paraview
polyConvert -V -o$MESH'InhomogenPLC' $MESH'Inhomogen'

# Generate the mesh.
tetgen -pazVAC -q1.2 $MESH'Inhomogen'

# Convert it to bms and vtk and remove temporary stuff.
meshconvert -vDBT -it -o $MESH'Inhomogen' $MESH'Inhomogen'.1
rm $MESH'Inhomogen'.1.*

# Look at mesh in paraview (make clip in y-normal direction).

# Now we create a resistivity map for the region marker 1 and 2
echo "1 10 # background region 1 has 10 Ohmm" > rho.map 
echo "2 100 # region 2 has 100 Ohmm" >> rho.map

dcmod -v -s modeltank.shm -o inhomogeneous -a rho.map $MESH'Inhomogen'

# We now have a homogeneous as well as an inhomogeneous result for our simulation.
# We can use the first to calculate the geometric factors to find the apparent resistivities for the second datafile.
dcedit -v -S -c homogeneous.collect -o modeltank.dat -f'a b m n rhoa k u i' inhomogeneous.ohm
# -c create geometric factor from the given collect file
# -S show a little bit statistics 

# For such kind of simulation the homogeneous part should be high accurate because it is usually needed once and delivers the geometric factors or maybe the primary potentials for further inversion. 
# You should think on quadratic shape function for the homogeneous mesh.
# If you want to invert the data you NEED to add noise.

# Alternatively, we can create a real cavity by changing the marker in polyCreateCube from -m to -H
# polyCreateCube -H mesh/cube # makes a hole
# Look now at the PLC and mesh in paraview (make a clip on y-plane).
# Compute and compare results.
# Change resistivity in other version. 
# Which value do we need to simulate a cavity well?

