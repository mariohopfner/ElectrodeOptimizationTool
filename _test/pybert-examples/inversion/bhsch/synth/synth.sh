#!/bin/bash
MESHGEN=dctriangle
QUALITY=34.3
VERBOSE='-v'

[ ! -d "pot" ] && mkdir pot
[ ! -d "mesh" ] && mkdir mesh

rm -rf pot/*
rm -rf mesh/*

MESH=mesh/world

polyCreateWorld -d2 -x 1000.0 -z 700.0 -m1 $MESH # // create world( 0--x, -z--0)
polyAddProfile -x 0 -z 0 -X 20 -Z 0 -n21 $MESH # // create 21 electrodes
polyRefineVIPS -z -0.1 $MESH # // refine all electrodes by adding a local sampling point in z-direction(0.1m)

echo "-50 -3" > layer.xy
echo "70 -3" >> layer.xy
echo "70 -2" >> layer.xy
echo "-50 -2" >> layer.xy
echo "-50 -3" >> layer.xy

polyAddProfile -i layer.xy $MESH
polyAddVIP -z -2.5 -m2 -R $MESH

$MESHGEN -$VERBOSE -q$QUALITY $MESH

meshconvert -v -p -D -d2 $MESH.bms
echo "1	100" > rho.map
echo "2	30" >> rho.map

dcmod $VERBOSE -a rho.map -s 21dd.shm -o pot/num $MESH.bms
dcedit -S -f'a b m n rhoa err k' -v -N -E -e3 -u 1e-5 21dd.ohm -o 21dd.dat
pyshowdata.py --sheme=DipolDipol 21dd.dat
