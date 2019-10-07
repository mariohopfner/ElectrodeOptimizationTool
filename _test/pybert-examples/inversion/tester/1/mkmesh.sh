addBox(){
x1=$1
x2=$2
z1=$3
z2=$4
marker=$5

echo "$x1 -$z1" > face.xz
echo "$x1 -$z2" >> face.xz
echo "$x2 -$z2" >> face.xz
echo "$x2 -$z1" >> face.xz
echo "$x1 -$z1" >> face.xz
polyAddProfile -i face.xz mesh/mesh
xm=`echo $x1 $x2|awk '{print ( $1 * 0.99 + $2 * 0.01 ) }'`
zm=`echo $z1 $z2|awk '{print ( $1 * 0.99 + $2 * 0.01 ) }'`
echo $xm $zm
polyAddVIP -R -m $marker -a1 -x $xm -y -$zm mesh/mesh
rm face.xz
}

mkdir -p mesh
polyCreateWorld -d2 -x30 -z15 -m1 mesh/mesh
polyTranslate -x2 mesh/mesh
addBox -1 5 0 2 2
addBox 1.5 2.5 0.5 1 3
addBox 1.5 2.5 1 1.5 4
echo 2.5 -1 > line.xz
echo 4 -1 >> line.xz
polyAddProfile -i line.xz -m1 mesh/mesh
head -n 7 tester.dat|tail -n 5 > elec.xz
polyAddVIP -m -99 -f elec.xz mesh/mesh
polyConvert -v -V mesh/mesh
dctriangle -v -q34.5 mesh/mesh
meshconvert -v -d2 -V mesh/mesh.bms