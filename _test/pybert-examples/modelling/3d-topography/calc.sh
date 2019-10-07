#!/usr/bin/env bash

# Define the usual preliminaries.
mkdir -p mesh

MESH=mesh/world
QUALITY=1.12

# Our digital elevation model is an equidistant grid of a 3x4 km region of a mountainous region with a spacing of 100m.
# A complete surface mesh of this topography is possible but lead to surface that is to fine in regions far from our measurement.
# We want a discretization that fits our needs for accuracy near to the electrodes and spare mesh cells in increasing distance but holds the coarse topography.
# We first create, as in Rücker et al. (2006), an unstructured surface mesh by Delaunay triangulation using Triangle. 
# This 2d mesh contains the electrode positions with a moderate local refinement but no height information, it is also large enough to span a greater area of the topography.
# The heights of this surface mesh, i.e., the z-coordinates will then be interpolated from the DEM mesh.
# This is done by createSurface, parameters are the surface 2d mesh quality and the size of the boundary around the electrodes.
# If a data file is provided to createSurface, the z-coordinates of electrode positions will be interpolated also.
# If heights are measured additionally they should be added to the elevation model since the ones in the data file are overridden.
# Please ensure that there are no duplicated coordinates in the topography file.
# The resulting 2D mesh contains the electrode positions with local refinement and is converted into a 3D PLC of a surface mesh and is called $MESH'Fine.poly'.
createSurface -vv -a topo.xyz -b5000 -q34.3 -d20 -S -o $MESH dipole17.shm
# -a additional points .. this should be the DEM file, if no -a is given the z-coordinates from the data file are taken
# -b boundary in % of maximal electrode distance
# -q 2d mesh quality
# -d local refinement in electrode vicinity [20m], i.e., 10% of the electrode distance
# -S smooth 2D mesh
# -v be verbose

# If you choose -v twice , e.g., -vv then createSurface generates a lot of debugging meshes that can be viewed with paraview.
# For instance:
# $MESH-MeshCoarse.vtk the whole surface mesh of all topographic points with the boundary
# $MESH-MeshFineFlath.vtk the 2D mesh with electrode positions and boundary without interpolation

# A new data file has been generated with the topography based on the DEM that needs a proper name
mv dipole17.shm.topo dipole17Topo.shm

# The created surface PLC must now be closed by closeSurface which makes a world box around it. 
closeSurface -v -z0 -o $MESH $MESH'Fine.poly'

# Refine each electrode by 10m in z-direction is not a bad idea
polyRefineVIPS -z -10.0 $MESH 

#The resulting PLC can be converted to VTK/STL using polyConvert and watched in paraview.
polyConvert -VS -o $MESH'PLC' $MESH

# The rest is the usual stuff: mesh generation and conversion including global p2 refinement:
tetgen -pazVAC -q$QUALITY $MESH # generate mesh
meshconvert -v -iT -BDVM -o $MESH $MESH.1 
python -c 'import pygimli as pg; m=pg.load("mesh/world.bms"); m=m.createP2(); m.save("mesh/world.bms");'

# -M write medit mesh file .. if you have the medit mesh viewer
rm $MESH.1.*

# Compute impedance for homogeneous resistivity of 1 Ohmm
dcmod -v -1 -s dipole17Topo.shm -o dipole17Topo $MESH
# -1 force all resistivity values to be 1

# Compute flat-earth geometric factor from original file
dcedit -v -f "a b m n k" -o dipole17HalfSpace.dat dipole17.shm

# Use the latter to compute apparent resistivity = topographic effect k_topo/k_flath
dcedit -vS -c dipole17HalfSpace.dat -f "a b m n rhoa k" -o dipole17Topo.data dipole17Topo.ohm
# -c use geometric factors from file

# The resulting apparent resistivity is the ratio of true and flat-earth geometric factor and thus the
# topography effect as defined by Rücker et al. (2006).
# For this example it is mostly around 1 but reaches deviations from -7% to +12%.
# data min = 0.935678, max = 1.12224 means (min-1)*100%=-7% and (max-1)*100%=12%
