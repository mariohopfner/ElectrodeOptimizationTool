#!/usr/bin/env bash

# Create a path for meshing stuff
mkdir -p mesh

# To spare some typing we define a variable for the resulting mesh
MESH=mesh/world

polyCreateWorld -d2 -x200 -z50 -m1 $MESH

# The geometry of the heterogeneity (the interface between the layers)
echo "-100 -1" > mesh/layer1.xy
echo "100 -1" >> mesh/layer1.xy
polyAddProfile -i mesh/layer1.xy $MESH

# Now define the lower layer (the background) as region with marker 2. 
polyAddVIP -z -1.05 -R -m2 $MESH

# Now we need to add 24 electrodes from [0.0, 0.0, 0.0] to [23.0 0.0, 0.0]
polyAddProfile -x0.0 -n 24 -X23.0 -m -99 $MESH

# create a rectangle shaped heterogeneity
echo "10 -2.9" > mesh/rect.xy
echo "15 -2.9" >> mesh/rect.xy
echo "15 -1.3" >> mesh/rect.xy
echo "10 -1.3" >> mesh/rect.xy
echo "10 -2.9" >> mesh/rect.xy
polyAddProfile -i mesh/rect.xy $MESH
polyAddVIP -x 12 -z -2.6 -R -m3 $MESH

# Electrodes need to be locally refined
polyRefineVIPS -z -0.1 $MESH

# create the mesh
dctriangle -v -q 34 -S $MESH

# To map the region marker to the desired resistivity values we have to create a rho.map file. 
# Here we map all cells with the region marker 1 to 10 Ohmm and all with region 2 to 100 Ohmm.
# Rectancle region(3) becomes to 20 Ohmm 
echo "1 10 "  > rho.map
echo "2 100" >> rho.map
echo "3 20" >> rho.map

# calculate real response
pytripatch -e mesh -d rho.map -E --label='Modell resistivity in $\Omega$m' $MESH.bms &
dcmod -a rho.map -s wa24.shm $MESH.bms -o wa24

# create complex rho map
echo "1 10 0 "  > crho.map
echo "2 100 0" >> crho.map
echo "3 20 -0.05" >> crho.map

# calculate complex response
dcmod -v -a crho.map -s wa24.shm $MESH.bms -o wa24c

# Finally we can convert the impedances into apparent resistivities.
dcedit -v -E -e1 -N -o wa24.dat wa24.ohm -f 'a b m n rhoa err ip k'
dcedit -v -E -e1 -N -o wa24c.dat wa24c.ohm -f 'a b m n rhoa err ip k'


# The resulting data can be viewed as pseudosection with pyshowdata.py.
# Please note that pyshowdata need some further improvements but give at least some first impressions.
#pyshowdata.py --scheme='WennerAlpha' wa24.dat






