#!/bin/bash
# Constants
DIA=0.06   # diameter
LEL=0.005  # length of electrode
DEL=0.05   # electrode spacing 
LSP=`echo $DEL $LEL|awk '{print $1 - $2}'`
echo $LSP  # length of piece between electrodes
SEG=16     # segments for cylinder
TOL=5e-3
SIZE=20
NEL=7      # number of electrodes
DEP=0.3525
#NEL=25      # number of electrodes
#DEP=1.25
# Temporary directory mesh
mkdir -p mesh
# Electrode surface
polyCreateCube -Z -s $SEG mesh/elec
polyAddVIP -H -z 0.001 mesh/elec
#polyAddVIP -R -m 3 -z 0.001 mesh/elec
polyTranslate -z 0.5 mesh/elec
polyScale -x $DIA -y $DIA -z $LEL mesh/elec
polyConvert -o mesh/elecPoly -V mesh/elec
# PVC space (hole) between electrodes
polyCreateCube -Z -s $SEG -m 0 mesh/blau
#polyAddVIP -R -m 2 mesh/blau
polyAddVIP -H mesh/blau
polyTranslate -z -0.5 mesh/blau
polyScale -x $DIA -y $DIA -z $LSP mesh/blau
polyConvert -o mesh/blauPoly -V mesh/blau
# start with pvc and add electrodes sequentially
cp mesh/blau.poly mesh/vestr.poly
for i in `seq 1 $NEL`
do
	DX=`echo $i $DEL|awk '{print ( $1 - 1 ) * $2}'`
	MA=`echo $i -9999|awk '{print $2 - $1}'`
	echo El $i DX $DX MA $MA
	cp mesh/elec.poly mesh/elec$i.poly
	polyAddVIP -B -m $MA mesh/elec$i
	polyAddVIP -m $i mesh/elec$i
	polyTranslate -z $DX mesh/elec$i
	polyConvert -V mesh/elec$i
	polyMerge -t $TOL mesh/vestr mesh/elec$i mesh/vestr
	DX=`echo $i $DEL|awk '{print $1 * $2}'`
	cp mesh/blau.poly mesh/blau$i.poly
	polyTranslate -z $DX mesh/blau$i
	polyConvert -V mesh/blau$i
	polyMerge -t $TOL mesh/vestr mesh/blau$i mesh/vestr
done
# Convert and mesh
polyConvert -V -o mesh/vestrPoly mesh/vestr
polyTranslate -z -$DEP mesh/vestr
polyCreateWorld -x $SIZE -y $SIZE -z $SIZE mesh/world
polyMerge mesh/world mesh/vestr mesh/mesh
tetgen -pazVACq1.12 mesh/mesh.poly
meshconvert -it -p -VMBD -o mesh/mesh mesh/mesh.1
rm mesh/mesh.1.*
# Calculation using finite elements with CEM
dcmod -v -1 -s ddwe7.shm mesh/mesh.bms # creates directly ddwe7.ohm
dcedit -vB -o ddwe7.data ddwe7.ohm     # adds k-factor and app. res.
