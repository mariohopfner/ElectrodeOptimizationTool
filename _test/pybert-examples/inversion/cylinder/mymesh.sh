MESH=mesh/mesh
polyCreateCube -v -Z -s 48 -m 2 $MESH # create unit cylinder with 48 segments
polyTranslate -z -0.5 $MESH           # moves it such that top is zero
polyScale -x 0.3 -y 0.3 -z 0.8 $MESH  # scale to radius 0.15 & height 0.8
cat soil_column.dat | head -n 82 |tail -n 80 > elec.xyz 
polyAddVIP -m -99 -f elec.xyz $MESH   # add electrodes to mesh
polyAddVIP -m -999 -x 0 -y 0 -z 0 $MESH # current reference node
polyAddVIP -m -1000 -x 0 -y 0 -z -0.8 $MESH # potential reference node
polyConvert -V -o $MESH-poly $MESH    # convert to vtk to load to paraview
