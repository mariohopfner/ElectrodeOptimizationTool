#!/usr/bin/env bash

# Create a path for the meshing stuff
mkdir -p mesh

# Defines how the PLC (*.poly) and the mesh (*.bms/vtk) will be called
MESH=mesh/world

# We define some parameter to keep this script flexible 
SIZE=100
LEN=10
RAD=0.05
SEG=16

# First, we create a world (a big box with appropriate boundary markers),
# big enough to ensure accurate solutions (10 times the electrode spread).
polyCreateWorld -x $SIZE -y $SIZE -z $SIZE -m1 $MESH
# We shift it upwards to let the electrodes be at zero level.
polyTranslate -z $[SIZE / 2] $MESH

# Next we create a cylinder by polyCreateCube -Z with $SEG segments.
# The -H option defines a hole marker, i.e., the interior will not be meshed.
# We rotate its x-axis towards x and scale it by its length $LEN and radius $RAD.
polyCreateCube -H -Z -s $SEG $MESH'cyl'
polyRotate -y 90 $MESH'cyl'
polyScale -x $LEN -y $RAD -z $RAD $MESH'cyl'

# We scale it again in y&z because (diameter=2*$RAD) and shift it down by $RAD
# to make it begin at the zero level (where the electrodes are in the file).
polyScale -y 2 -z 2 $MESH'cyl'
polyTranslate -z -$RAD $MESH'cyl'
# To be sure to apply the right dimension take a look with your preferred VTK viewer.
polyConvert -V $MESH'cyl'

# Finally we merge the PLC files.
polyMerge $MESH $MESH'cyl' $MESH

# The electrodes were extracted from the data file and put into the mesh.
# Note. If such auto generation fail, check the file format and/or the unix style line carriage return, i.e., make a dos2unix before.
nElecs=`head -n 1 data.shm | cut -d'#' -f1`
head -n $[nElecs + 2] data.shm | tail -n $nElecs > mesh/elecs.xyz
polyAddVIP -f mesh/elecs.xyz -m -99 $MESH

# We can export it as VTK to control the whole geometry and the electrodes (spherical glyphs with scaling 0.0005)
polyConvert -V -o $MESH'PLC' $MESH

# We then refine them by 1/10 electrode distance to ensure an accurate solution.
polyRefineVIPS -x 0.0015 $MESH

# Finally, the PLC is need to be meshed by TetGen and refined quadratically to be accurate.
tetgen -pazVACq1.3 $MESH
meshconvert -v -it -BDV -o $MESH $MESH.1
python -c 'import pygimli as pg; m=pg.load("mesh/world.bms"); m=m.createP2(); m.save("mesh/worldPrim.bms");'

rm -rf $MESH.1.*

# At the end, we can call the actual modelling by
dcmod -v -1 -s data.shm $MESH'Prim'

# As a result, we have the resistances for a constant resistivity of 1 Ohmm (-1)
# in the file data.ohm.
# The inverse of this resistances is the geometric factor.
# We could now extract it using Python or Matlab, plot and so on.
# We can also apply it using dcedit -c (correct) to any data file.
# It we apply it to itself by typing (-o means output and -f tokes to be saved)
dcedit -v -c data.ohm -o one.dat -f "a b m n rhoa k" data.ohm

# We obtain a file of apparent resistivity equal to one and the numerically
# calculated geometric factor. For any other data we could also use -c one.dat.