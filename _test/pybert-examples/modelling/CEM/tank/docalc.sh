# run this to perform all calculations

sh mkpolyE.sh
MESH=mesh/mesh
QUALITY=1.2
tetgen -pazVACq$QUALITY $MESH
meshconvert -v -o $MESH -iT -VMBD $MESH.1
rm $MESH.1.*

for ci in 1e-6 1e6; do
    rm -f contactImpedance.map
    touch contactImpedance.map
    for i in `seq 1 100`; do 
        echo "$i $ci" >> contactImpedance.map
    done  
    dcmod -v -1 -s data.shm mesh/mesh
    mv data.ohm dataE$ci.ohm 
done

for p in 0 1 2 3 1.5; do
    sh mkmeshPX.sh $p
    dcmod -v -1 -s data$p.shm meshP$p/mesh.bms
    dcedit -vSBD -c dataE1e-6.ohm -o effect$p.data data$p.ohm
done
