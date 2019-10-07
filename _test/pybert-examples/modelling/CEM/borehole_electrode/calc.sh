#!/bin/bash

source polyScripts.sh

mkdir -p mesh
mkdir -p pot

MESH=mesh/world

createMesh(){
    echo cem=$cem
    polyCreateWorld -x 300 -y 300 -z 200 -m1 $MESH
    if [ $cem -eq 1 ]; then
        polyScriptAddCEM ID=0 x=0.0 y=0.0 z=0.0 dx=0.1 dz=10.0 nx=0.0 ny=0.0 nz=-1.0 cyl=8
    else
        polyAddVIP -m -99 $MESH
    fi
    
    polyCreateCube -m2 cube
    polyScale -y 20 -z 5 cube
    polyTranslate -x 5 -z -8 cube
    polyRotate -L -y 45 cube
    polyMerge $MESH cube $MESH

    polyAddProfile -x 1.0 -X 20 -n20 -m -99 $MESH
    polyRefineVIPS -r0.05 $MESH

    polyConvert -V -o ${MESH}-poly $MESH 

    tetgen -pazVACq1.25 $MESH

    meshconvert -p -v -o $MESH -iT -MBD $MESH.1

    rm $MESH.1.*
}

echo "1 100 # background" > rho.map
echo "2 1 # inhom" >> rho.map

for cem in 0 1
do

createMesh 

dcmod -v -1 -V -p pot/num -o hom$cem $MESH
dcmod -v -a rho.map -V -p pot/num -o inhom$cem $MESH

#dcmod -v -a rho.map -V -p pot/num -s 21cpp.shm -o inhom$cem $MESH
#dcedit -v -BS -c hom.collect -o inhom$cem.data inhom$cem.ohm

done

