#!/usr/bin/env bash

# For every modelling, aka simulation, we need a proper mesh that contains all needed geometrical information.
# See mkmesh.sh for more useful information on how to create a suitable mesh.
# We need to call this script because it generates mesh/world.bms. Its sufficient to call this just once. ;)
bash mkmesh.sh

# Now we can perform the first finite element modelling using dcmod for our simple world model.
# On default, dcmod simulates current injection on every known electrode node and calculates the total field potential (TP) at every electrode else.
# The output is a collect-file (result.collect), i.e., the whole potential matrix.
# The values in the main diagonal (potential at the current injection) are arbitrary, but the side diagonals
# should hold the theoretical value of 1/(2*pi)=0.15915494309190 for a=1m electrode distance, e.g., collect[0][1].
# The matrix is symmetric for total field calculation.
# After Rücker et al. (2006) the accuracy by spatial refinement of a/10 and quadratic shape functions should be
# far below 1%.
dcmod -v -o result mesh/world.bms
# -v be verbose
# -o output filename (.collect is added automatic)
# mesh/world.bms to be processed

# Alternatively to the total potential calculation is the secondary potential (SP) modelling. SP is much more accurate than TP but can only # applied if there are heterogeneities and half-space geometry.
# As our model itself is homogeneous, the secondary potential is zero and the primary is the analytical solution.
dcmod -v -o resultSP -S mesh/world.bms
# -S use singularity removal for secondary potential calculation

# If the potentials itself are to be observed, the -p switch needs to be added.
# That saves the potentials in a file pot.bmat, which can be read by python or matlab or another dcmod call.
# If the switch -V is added then for each electrode a potential file pot.x.pot is created that can be viewed.
dcmod -v -p pot -V mesh/world.bms
# -p save the full potential matrix
# -V save potentials in vector form

# For a first view using paraview, you can use meshconvert.
# Probably the binary vector files written by dcmod cannot be read by meshconvert directly due to the vintage of meshconvert.
# To avoid meshconvert behaves odd we convert the binary file into ascii using pygimli and convert them back from ascii format into binary using va2b that is also vintage like meshconvert.
#
# This procedure seems weired but works and the resulting mesh/pot.0.vtk contains the potential for current injection at electrode 0 and can be viewed in paraview. (Better use a logarithmic colorbar)
# Generally the usage of pygimli is recommended for more control of the post processing.
python -c 'import pygimli as pg; v = pg.RVector("pot.0.pot", pg.Binary); v.save("tmp.vec");'
va2b tmp.vec
meshconvert -v -b tmp.vec -V -o mesh/pot0 mesh/world.bms
# -b binary vector to be added to the vtk

# If you want apparent resistivities (rhoa) from your simulation you can filter them manually out of the collect file potential matrix or you can let dcmod do that for you.
# To define what kind of measurements your want to filter you need to define a scheme-file in the gimli unified data format (http://www.resistivity.net/index.php?id=unidata&type=1) and provide that scheme-file to dcmod.
dcmod -v -s dipdip.shm mesh/world.bms
# -s scheme file to filter the collect matrix

# The result of this calculation is an ohm-file dipdip.ohm (unless otherwise defined by -o) in the gimli unified data format containing impedances in Ohm. i.e., u_simulated/i_simulated while i_simulated is 1 ampere.
# We calculated one measurement for homogeneous 1 Ohm m, that should be the inverse of the geometric factor 1/G.
# with G = -pi * n * (n+1) * (n+2) * a
# in our case 1/(-pi*9*10*11*1) = 1/(pi*990) = -1/3310.177 = -3.2153e-4

# The impedance values can be transformed into apparent resistivities using dcedit.
# The necessary geometric factors are determined automatic.
dcedit -v -o dipdip.dat -f 'a b m n rhoa r k' dipdip.ohm
# -v be verbose
# -o output filename
# -f output format
# dipdip.ohm ohm file to be processed

# The final result is dipdip.dat that contains the rhoa we are locking for.

# The whole thing is even easier and provide a lot more control and post processing ability directly in Python using pygimli/pybert.
# See calc.py for example code and documentation.
