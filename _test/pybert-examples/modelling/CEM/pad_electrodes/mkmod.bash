MESH=cube   # name of the file
LENGTH=0.1  # length of the box
WIDTH=0.06  # width of the box
HEIGHT=0.03 # height of the box
RAD=0.002   # radius of pads
DX=0.02     # electrode distance
DIST=0.02   # distance edge to first electode
polyCreateCube $MESH  # unit cube around the origin
polyAddVIP -m -999 $MESH  # reference current electrode (needed for CEM)
polyTranslate -x 0.5 -z -0.5 $MESH  # start at x=0 and z=0
polyScale -x $LENGTH -y $WIDTH -z $HEIGHT $MESH # scale to real size
polyTranslate -x -$DIST $MESH  # shift so that first electrode is at x=0
python <<END
import pygimli as pg
circle = pg.meshtools.createCircle(pos=(0, 0), radius=$RAD, segments=8)
pad = pg.meshtools.createMesh(circle, quality=34, smooth=[1, 10])
pad3d = pg.Mesh(3)
pad3d.createHull(pad)
pad3d.exportAsTetgenPolyFile('pad3d.poly')
END
source polyScripts.sh # enables calling polyScriptAddCEM
echo 4 > data.shm # create new scheme file with four electrodes
echo "#x y z" >> data.shm  # positions
for i in 0 1 2 3;do
    x=`echo $i $DX | awk '{print $1*$2}'`
    echo $x 0 0 >> data.shm # electrode position
    polyScriptAddCEM ID=$i x=$x nz=1 shape=pad3d.poly # add CEM electrode
done
polyConvert -V -o $MESH-poly $MESH  # creates cube-poly.vtk
tetgen -pazVACq1.2 $MESH.poly  # meshes the PLC
meshconvert -v -it -VMBD -o $MESH $MESH.1  # convert into BMS+VTK
echo 2  >> data.shm # two measurements
echo "#a b m n" >> data.shm # token list
echo "1 2 4 3" >> data.shm  # dipole-dipole
echo "1 4 2 3" >> data.shm  # Wenner
dcmod -v -D -1 -s data.shm $MESH.bms
dcedit -v -f "a b m n r k rhoa" data.ohm # computes apparent resistivity=geometric effect
tail -n2 data.ohm.edt  # show last lines
