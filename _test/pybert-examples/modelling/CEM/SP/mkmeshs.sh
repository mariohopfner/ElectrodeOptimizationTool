mkdir -p mesh # create mesh directory if not existent
# a few definitions
DIA=5 # diameter of boreholes
SEG=8 # segments for cylinder
MESH=mesh/mesh
ELEC=mesh/electrode
CUBE=mesh/cube
# position and length of boreholes
posx=(-200 -200 200 200)
posy=(-200 200 -200 200)
len=(100 100 100 100)
# big box with Neumann (top) and mixed boundary conditions
polyCreateWorld -x 1000 -y 1000 -z 500 -m 1 $MESH
# anomalous cube
polyCreateCube -m 2 $CUBE
polyTranslate -z -0.5 $CUBE
polyScale -x 100 -y 100 -z 50 $CUBE
polyTranslate -z -100 $CUBE
polyMerge $MESH $CUBE $MESH
NEL=${#posx[*]} # number of electrodes
IND=10000       # running index for numbering CEM electrodes
echo $NEL > data.shm
echo "#x y z" >> data.shm
for i in `seq 0 $[NEL - 1]`
do
    echo $IND ${posx[i]} ${posy[i]} ${len[i]}
    polyCreateCube -H -Z -s $SEG $ELEC # create cylinder
    polyAddVIP -B -m -$IND $ELEC # add boundary CEM marker
    polyTranslate -z -0.5 $ELEC  # shift to match top=zero
    polyScale -x $DIA -y $DIA -z ${len[i]} $ELEC # scale to length
    polyTranslate -x ${posx[i]} -y ${posy[i]} $ELEC # shift to position
    polyMerge $MESH $ELEC $MESH # merge electrode into mesh
    IND=$[IND + 1] # increment CEM index
    echo ${posx[i]} ${posy[i]} 0 >> data.shm
done
echo 1 >> data.shm
echo "#a b m n" >> data.shm
echo 1 2 3 4 >> data.shm
polyConvert -V -o $MESH-poly $MESH # create VTK mesh/mesh-poly.vtk from PLC
tetgen -pazVACq1.2 $MESH # mesh with options
meshconvert -vBDMV -it -o ${MESH}S $MESH.1  # no refinement: S
meshconvert -vpBDMV -it -o ${MESH}P $MESH.1 # p refinement:  P
rm $MESH.1.*