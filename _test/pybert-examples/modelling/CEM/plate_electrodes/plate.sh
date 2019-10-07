#!/usr/bin/python
# -*- coding: utf-8 -*-

mkdir -p mesh

MESH=mesh/world
SIZE=1000
depth=1.0
len2=0.3 # 0.2x0.2m plate

polyCreateWorld -d3 -x $SIZE -y $SIZE -z $SIZE -m1 $MESH
polyScale -z 0.6 $MESH
for i in `seq 13`
do
	marker=-$[i+9999]
	echo "cem: " $i
	#python << END
	#from pygimli.polytools import polyAddRectangle, Rectangle
	#polyAddRectangle(  "mesh/world", Rectangle( [$i, 0], [0.2,0.2] ), $marker )
	#END
	# create xy file (5 lines - closed)
	echo $i $len2 | awk '{print $1-$2, -$2}' > __pad.xy
	echo $i $len2 | awk '{print $1-$2, $2}'  >> __pad.xy
	echo $i $len2 | awk '{print $1+$2, $2}'  >> __pad.xy
	echo $i $len2 | awk '{print $1+$2, -$2}' >> __pad.xy
	echo $i $len2 | awk '{print $1-$2, -$2}' >> __pad.xy
	polyCreateWorld -d2 -t __pad.xy -C __pad
	dctriangle -v -q34.5 -S __pad # -a ??
	polyCreateFacet -o __pad3d -m $marker __pad.bms
#	polyTranslate -z -$depth __pad3d
#	polyAddVIP -x $i -z -0.1 -m 0 mesh/world
	polyMerge mesh/world __pad3d mesh/world
done
rm __*

#polyCreateWorld -x 60 -z 60 -d2 mesh/layer
#polyCreateFacet -o mesh/layer3d mesh/layer.poly
#polyTranslate -y 30 -z -1.0 mesh/layer3d
#polyMerge mesh/world mesh/layer3d mesh/world

polyConvert -V -o $MESH-poly.vtk $MESH
rm -f $MESH.1.*
tetgen -d $MESH
if [ -f $MESH.1.face ]
then
	meshconvert -V -it -o invalid $MESH.1
else
	tetgen -gpazACq1.20 $MESH
	meshconvert -p -v -DMV -o $MESH.bms -it $MESH.1
fi

dcmod -v -s 13dd.shm $MESH.bms
dcedit -vSB -o 13dd.data 13dd.ohm

#python << END
#import pygimli as g
#mesh = g.Mesh( "mesh/world.bms")
#for c in mesh.cells():
#	if c.center()[2] < -depth:
#		c.setAttribute(1.0)
#		c.setMarker(1)
#	else:
#		c.setMarker(2)
#		c.setAttribute(2.0)
#
#mesh.save( "mesh/world.bms")
#mesh.exportVTK( "mesh/world-mapped")
#mesh.exportBoundaryVTU( "mesh/worldBC")
#
#END
