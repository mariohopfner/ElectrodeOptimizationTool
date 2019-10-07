#!/bin/bash

source polyScripts.sh
QUALITY=$1
[ -n "$QUALITY" ] && QUALITY=1.25
MESH=mesh/mesh
mkdir -p mesh
polyCreateCube -m 1 -a 1e-4 $MESH # creates unit cube
polyTranslate -x 0.5 -y 0.5 -z 0.5 $MESH # translates to origin=corner

len=0.03
thk=0.01
segments=8
count=0

cat data.shm |head -n 102|tail -n 100 | while read x y z marker; do
    [ $x == 0.0 ] && nx=1  && ny=0
    [ $x == 1.0 ] && nx=-1 && ny=0
    [ $y == 0.0 ] && ny=1  && nx=0
    [ $y == 1.0 ] && ny=-1 && nx=0
  
    polyScriptAddCEM ID=$count x=$x y=$y z=$z dx=$thk dz=$len nx=$nx ny=$ny nz=0 cyl=$segments
    count=$[ count + 1 ]
      
done
polyConvert -V -o ${MESH}Poly $MESH 

polyAddVIP -x 0.5 -y 0.5 -z 0 -m -999 $MESH # current reference
polyAddVIP -x 0.51 -y 0.5 -z 0 -m 0 $MESH # local refine current reference
polyAddVIP -x 0.5 -y 0.5 -z 1 -m -1000 $MESH # potential reference
polyAddVIP -x 0.51 -y 0.5 -z 1 -m 0  $MESH # local refine potential reference

