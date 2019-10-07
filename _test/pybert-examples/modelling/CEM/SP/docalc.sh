mkdir -p pot
# calculate potentials for 1 Ohmm on P mesh and interpolate to S mesh
dcmod -v -1 -m mesh/meshS.bms -o pot/pot -p pot/pot mesh/meshP.bms
# create resistivity map and use it for secondary potential calculation
echo 1 100 > rho.map
echo 2 10 >> rho.map
dcmod -v -S -a rho.map -x pot/pot -s data.shm -o out mesh/meshS.bms
# filter output using the geometric factors=1/u(1) from the P run
[ -f out.ohm ] && dcedit -vSB -c pot/pot.collect -o out.data out.ohm