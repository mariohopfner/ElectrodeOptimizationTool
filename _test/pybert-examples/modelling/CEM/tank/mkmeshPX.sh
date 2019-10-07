#!/bin/bash
DX=$1
LEFT=`echo $DX|awk '{print $1 / 100}'`
RIGHT=`echo $DX|awk '{print 1 - $1 / 100}'`
elecs=`echo elec$DX|tr . _`.xyz
echo $LEFT $RIGHT $elecs

cat data.shm |head -n 102|tail -n 100 |
sed "s/0\.0/$LEFT/g"|
sed "s/1\.0/$RIGHT/g" > $elecs

nl=`cat data.shm|wc -l`
cat data.shm |head -n 2 > data$DX.shm
cat $elecs >> data$DX.shm
cat data.shm| tail -n $[nl - 102] >> data$DX.shm

mkdir -p meshP$DX

MESH=meshP$DX/mesh
polyCreateCube -m 1 -a 1e-4 $MESH # creates unit cube
polyTranslate -x 0.5 -y 0.5 -z 0.5 $MESH # translates to origin=corner

polyAddVIP -f $elecs -m -99 $MESH # add electrodes to mesh
polyRefineVIPS -z -0.01 $MESH

polyAddVIP -x 0.5 -y 0.5 -z 0 -m -999 $MESH # current reference
polyAddVIP -x 0.51 -y 0.5 -z 0 -m 0 $MESH # local refine current reference
polyAddVIP -x 0.5 -y 0.5 -z 1 -m -1000 $MESH # potential reference
polyAddVIP -x 0.51 -y 0.5 -z 1 -m 0  $MESH # local refine potential reference

polyConvert -V -o $MESH-poly $MESH
tetgen -pazVACq1.12 $MESH
meshconvert -p -v -o $MESH -iT -MBD $MESH.1
rm $MESH.1.*
rm $elecs