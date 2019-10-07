
addBox(){
x1=$1
x2=$2
z1=$3
z2=$4
maker=$5

echo "$x1 -$z1" > face.xz
echo "$x1 -$z2" >> face.xz
echo "$x2 -$z2" >> face.xz
echo "$x2 -$z1" >> face.xz
echo "$x1 -$z1" >> face.xz
polyAddProfile -i face.xz mesh/mesh
polyAddVIP -R -m $maker -a1 -x $x1.1 -y -$z1.1 mesh/mesh
rm face.xz
}

createParaMesh -v -d 2 -A -S -E -z 6.62641 -b 500 -p 5 -l 0.25 -a 0 -q 34.0 -o mesh/mesh ../21dd.dat

addBox 9.5 10.5 3 4 3