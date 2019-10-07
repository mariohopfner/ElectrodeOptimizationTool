#!/usr/bin/env bash

# Utility script to create a PLC for our experimental tank don't call it directly without argument. See calc.sh
MESH=$1

# In comparison to a simulation of field measurements a experimental tank have well defined spatial dimensions and needs different boundary conditions (BC).
# There is no current flow through the tanks boundary at all, so homogeneous Neumann BC have to be defined.
# Luckily this kind of natural BC are the default for finite element simulations. 
# We just need to define a base cube with a desired marker and scale and translate them to fit the spatial requirements.
# polyCreateCube generates the PLC for a unit cube symmetric around origin.
# Note, the region marker lies in the origin. (TODO We need to unify this on poly tool rewrite) 
# If this leads to problems you can add manually a new region marker, when a region have two marker the later stands.
polyCreateCube -m 1 $MESH

# Move the tank such that it goes from x/y=[0 to 1]
polyTranslate -x 0.5 -y 0.5 $MESH

# Scale the tank such that it's dimension is 0.99m x 0.5m x 1m
polyScale -x 0.99 -y 0.5 $MESH

# Our electrode positions are defined in the scheme file so we extract them from there instead of setting all 48 electrodes manually.
# Assuming a standard layout of the scheme file we can extract the electrode positions into a file mesh/elec.xyz.
nElecs=`head -n 1 modeltank.shm | cut -d'#' -f1`
head -n $[nElecs + 2] modeltank.shm | tail -n $nElecs > mesh/elec.xyz

# We add our electrode positions into the tank and define them to be electrodes by setting the marker -99.
polyAddVIP -m -99 -f mesh/elec.xyz $MESH 
#-f read electrode positions from file

# There are two small problems to overcome by simulations of domains with pure homogeneous Neumann BC.
# Firstly, we need always dipole current injection (usually dcmod perform internal only pol injections) because there can be no current flow since we forbid the flow through the boundaries.
# We need to define a reference electrode position inside the PLC so dcmod will perform dipole measurements against this reference and can provide in the later the usual potential matrix. 
# A reference electrode is marked with -999 and should be somewhere away from the common electrodes.
polyAddVIP -x 0.5 -y 0.5 -z -0.5 -m -999 $MESH

# The second problem for pure Neumann domains is the non-uniques of the partial differential equation due to the lack of any calibration. 
# We add a necessary calibration node where the potentials at this position forced to be 0.0. 
# This node need the marker -1000 and should be somewhere on the boundary far from the electrodes.
polyAddVIP -x 0.75 -y 0.25 -z 0.5 -m -1000 $MESH

# Finally we refine all electrodes by additional points of 1/2 mm distance in -z-direction.
polyRefineVIPS -z -0.0005 $MESH 
