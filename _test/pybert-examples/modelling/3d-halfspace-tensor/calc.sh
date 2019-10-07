#!/usr/bin/env bash

mkdir -p mesh
MESH=mesh/world

# start with creating a PLC
SIZE=200
polyCreateWorld -x $SIZE -y $SIZE -z $SIZE -m 1 $MESH
polyScale -x 2 -y 2 mesh/world

# first cube
polyCreateCube -m 2 $MESH'cube'
polyTranslate -x -0.5 -z -0.50 $MESH'cube'
polyScale -x 25 -y 25 -z 25 $MESH'cube'
polyConvert -v -V -o $MESH'cubePLC' $MESH'cube'

# merge cubes with plc
polyMerge -v $MESH $MESH'cube' $MESH

# add electrodes
nElecs=`head -n 1 _test.shm | cut -d'#' -f1`
head -n $[nElecs + 2] _test.shm | tail -n $nElecs > mesh/elecs.xyz

polyAddVIP  -m -99 -f mesh/elecs.xyz $MESH

# creates vtk for inspection
polyConvert -V -o $MESH'PLC' $MESH
# refine electrodes with 1/10 electrode spacing
polyRefineVIPS -z -0.01 $MESH

# build the mesh
tetgen -pazVACq1.2 $MESH
meshconvert -v -iT -BDV -o $MESH $MESH.1
python -c 'import pygimli as pg; m=pg.load("mesh/world.bms"); m=m.createP2(); m.save("mesh/world.bms");'

rm -rf $MESH.1.*

echo "1 10 # Background" > rho.map
echo "2 10 # Body" >> rho.map

# calculate fem solution using BERT
dcmod -v -a rho.map -s _test.shm $MESH
dcedit -v -B -o _test.data _test.ohm

