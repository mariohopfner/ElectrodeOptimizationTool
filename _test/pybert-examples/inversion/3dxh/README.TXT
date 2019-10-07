This represents a 3D crosshole experiment provided by J. Doetsch from ETH Zurich.
4 Boreholes with 0.7m spaced electrodes between 4 and 9m depth have been installed.
Crosshole bipole-bipole measurements were applied between each two boreholes and
are 3D interpreted. As in the 2dxh example, we use the polyFlatWorld script for
creating the PLC using the PARAGEOMETRY key. So the cfg file reads

DATAFILE=3dxh.ohm
DIMENSION=3
PARABOUNDARY=15      # a little bit bigger than default
PARAGEOMETRY="polyFlatWorld $DATAFILE"  # for flat cross-hole geometry
ZWEIGHT=0.2         # enhance vertically layered structures

