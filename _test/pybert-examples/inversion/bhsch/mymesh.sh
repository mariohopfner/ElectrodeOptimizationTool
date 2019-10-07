createParaMesh -v -d 2 -A -S -E -z 70 -b 2000 -p 10 -l $PARADX -a $PARAMAXCELLSIZE -q 34.0 -o mesh/mesh $DATAFILE
x1=150
x2=160
z1=4
z2=14
BOXAREA=30
echo $x1 -$z1 > face.xz
echo $x1 -$z2 >> face.xz
echo $x2 -$z2 >> face.xz
echo $x2 -$z1 >> face.xz
echo $x1 -$z1 >> face.xz
polyAddProfile -i face.xz mesh/mesh
polyAddVIP -R -m 3 -a $BOXAREA -x $x1.1 -y -$z1.1 mesh/mesh
z1=$z2
z2=23
echo $x1 -$z1 > face.xz
echo $x1 -$z2 >> face.xz
echo $x2 -$z2 >> face.xz
echo $x2 -$z1 >> face.xz
echo $x1 -$z1 >> face.xz
polyAddProfile -i face.xz mesh/mesh
polyAddVIP -R -m 4 -a $BOXAREA -x $x1.1 -y -$z1.1 mesh/mesh

echo "120 -14" > face.xz
echo "150 -14" >> face.xz
polyAddProfile -i face.xz mesh/mesh
echo "160 -14" > face.xz
echo "190 -14" >> face.xz
polyAddProfile -i face.xz mesh/mesh
echo "120 -23" > face.xz
echo "150 -23" >> face.xz
#polyAddProfile -i face.xz mesh/mesh
echo "160 -23" > face.xz
echo "190 -23" >> face.xz
#polyAddProfile -i face.xz mesh/mesh
echo "120 -32" > face.xz
echo "150 -32" >> face.xz
polyAddProfile -i face.xz mesh/mesh
echo "160 -32" > face.xz
echo "190 -32" >> face.xz
polyAddProfile -i face.xz mesh/mesh


z1=$z2
z2=32
echo $x1 -$z1 > face.xz
echo $x1 -$z2 >> face.xz
echo $x2 -$z2 >> face.xz
echo $x2 -$z1 >> face.xz
echo $x1 -$z1 >> face.xz
polyAddProfile -i face.xz mesh/mesh
polyAddVIP -R -m 5 -a $BOXAREA -x $x1.1 -y -$z1.1 mesh/mesh
z1=$z2
z2=45
echo $x1 -$z1 > face.xz
echo $x1 -$z2 >> face.xz
echo $x2 -$z2 >> face.xz
echo $x2 -$z1 >> face.xz
echo $x1 -$z1 >> face.xz
polyAddProfile -i face.xz mesh/mesh
polyAddVIP -R -m 6 -a $BOXAREA -x $x1.1 -y -$z1.1 mesh/mesh
