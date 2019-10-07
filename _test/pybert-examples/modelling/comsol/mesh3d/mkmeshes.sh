#!/usr/bin/env bash

DX=0.03
QU=1.13

cp mysurface.poly mesh.poly
polyConvert -V -o meshPoly mesh
polyRefineVIPS.exe -z -$DX mesh
tetgen -VACpazq$QU mesh

meshconvert -v -p -iT -VDBM -o mesh mesh.1
#meshconvert -v -p -iT -VDBM -o meshP2 mesh.1
rm mesh.1.*

#bms2vtk -H -o mymeshH2.bms mymesh.bms
#bms2vtk -H -o mymeshH3.bms mymeshH2.bms
#bms2vtk -P -o mymeshH2P2.bms mymeshH2P2.bms
#bms2vtk -P -o mymeshP2.bms mymesh.bms
