This example is about a cylindrical model tank used at the BGR Hannover by
M. Furche. First we write a script mymesh.sh that describes the geometry

MESH=mesh/mesh
polyCreateCube -v -Z -s 48 -m 2 $MESH # create unit cylinder with 48 segments
polyTranslate -z -0.5 $MESH           # moves it such that top is zero
polyScale -x 0.3 -y 0.3 -z 0.8 $MESH  # scale to radius 0.15 & height 0.8
cat soil_column.dat | head -n 82 |tail -n 80 > elec.xyz 
polyAddVIP -m -99 -f elec.xyz $MESH   # add electrodes to mesh
polyAddVIP -m -999 -x 0 -y 0 -z 0 $MESH # current reference node
polyAddVIP -m -1000 -x 0 -y 0 -z -0.8 $MESH # potential reference node
polyConvert -V -o $MESH-poly $MESH    # convert to vtk to load to paraview 

We include this into the cfg-file using the PARAGEOMETRY key:

DATAFILE=soil_column.dat
DIMENSION=3
TOPOGRAPHY=1
CYLINDER=1   # defines a closed geometry
PARAGEOMETRY=mymesh.sh
PRIMDX=0.01
PRIMP2MESH=1

The result shows the resistivity and phase distribution in the column.
In the next step we introduce the time lapse data in 0.dat-5.dat into the cfg
file using TIMESTEPS=timesteps.txt holding the names of the data files.
The resulting resistivity ratios are more significant than the absolute values
and show the downward-moving water front and the beginning dry-out.
