from __future__ import print_function  # make it Python 2 compatible
from math import ceil, floor
import pygimli as pg
import numpy as np


data = pg.DataContainer('2dxh.dat')
spos = data.sensorPositions()
xmin = spos[0][0]
xmax = spos[-1][0]
dx = 0.05
zmax = ceil(2.0 / dx) * dx
xb = (xmax-xmin)*0.15/100
xbmin = floor((xmin - xb) / dx) * dx
xbmax = ceil((xmax + xb) / dx) * dx
print((xmin, xmax, dx, zmax))

x = np.arange(xbmin, xbmax, dx)
z = np.arange(-zmax, dx, dx)
print((x, z))

mesh = pg.Mesh()
mesh.create2DGrid(x, z)
for c in mesh.cells():
    c.setMarker(2)

mesh2 = pg.meshtools.appendTriangleBoundary(mesh, 50., 50.)
mesh2.save('mesh/mesh.bms')
