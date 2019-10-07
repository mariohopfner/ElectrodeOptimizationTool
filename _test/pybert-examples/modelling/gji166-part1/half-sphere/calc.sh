#!/usr/bin/env bash

# Define the usual preliminaries.
mkdir -p mesh

MESH=mesh/world
QUALITY=1.2

MESHGEN=tetgen
#MESHGEN=tetgen1.2.3-r3
#MESHGEN=tetgen1.3-r1
#MESHGEN=tetgen1.3.3
#MESHGEN=tetgen-1.3.2
BOUNDARY=20

# Create our world
polyCreateWorld -x $BOUNDARY -y $BOUNDARY -z `echo "$BOUNDARY * 0.7" | bc` -m1 $MESH

# We need to convert the half sphere stl into a valid PLC for TetGen
polyConvert -P -o mesh/halfsphere halfsphere.stl

# The half sphere have an extend of x=[0., 3.0], y=[0.,3.], z=[1.5.,3.] and need to be scaled and rotated

# Move the center to [0.0, 0.0, 0.0]
polyTranslate -x -1.5 -y -1.5 -z -1.5 mesh/halfsphere
# Rotate it top->down
polyRotate -x 180 mesh/halfsphere
# Rotate it 90 Degrees. This was necessary for older TetGen versions, maybe obsolete
polyRotate -z 90 mesh/halfsphere
# Scale it by 2/3 to diameter 2, i.e, radius = 1m
polyScale -x 0.66666667 -y 0.66666667 -z 0.66666667 mesh/halfsphere
# Scale it 2.25, i.e, radius = 2.25m
polyScale -x 2.25 -y 2.25 -z 2.25 mesh/halfsphere

# Region marker 2 for the half sphere
polyAddVIP -x 0.0 -y 0.0 -z -0.1 -m 2 -R -a 0.0 mesh/halfsphere

# Merge world and half sphere
polyMerge $MESH mesh/halfsphere $MESH

# Add 21 electrodes from [0.0, -5.0, 0.0] to [0.0, 5.0, 0.0]
polyAddProfile -x 0.0 -y -5.0 -z -0.0 -X 0.0 -Y 5.0 -Z 0 -n 21 -m-99 $MESH

# optionally refine
#polyRefineVIP -x 0.01 $MESH

# Create VTK for visual feedback of the PLC
polyConvert -V -o $MESH'PLC' $MESH

$MESHGEN -pafzACVT1e-10q$QUALITY $MESH

# Create VTK and medit-file for visual feedback of the mesh, the 
meshconvert -B -d3 -v -iT -Y -V -M -o $MESH $MESH.1
rm $MESH.1*

echo "1 10" > rho.map 
echo "2 1" >> rho.map

# we create a pole-pole configuration scheme file on the fly
pycreateshm --scheme='pp' -A -m $MESH.bms -o pp.shm
dcmod -v -S -s pp.shm -a rho.map $MESH.bms
dcedit -v pp.ohm -f'a b m n rhoa err k' -o pp.dat

# filterdata -o $MESH'PP.dat' num.collect
# 
# tail -n $[`head -n1 $MESH'PP.dat'`-1] $MESH'PP.dat' | cut -f5 > aPP.dat
# tail -n $[`head -n1 $MESH'PP.dat'`-1] $MESH'PP.dat' | cut -f3 > koord.dat
# 
# paste ana.dat aPP.dat | awk '{printf("%f\n", (($2/$1)-1)*100)}' > err.dat
# paste koord.dat ana.dat aPP.dat err.dat > all.data
# 
# paste all.data reciprocity.data > allWithRez.dat
