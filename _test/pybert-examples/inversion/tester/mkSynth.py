#!/usr/bin/env python

import sys, os

import pygimli as pg
import pygimli.paratools

grid = g.createMesh2D(6, 4)
grid.translate([-1.0, -4.0, 0.0]) 

for c in grid.cells():
    if c.center()[1] > -1:
        c.setMarker(2)
    else:
        c.setMarker(3)

mesh = pygimli.paratools.appendTriangleBoundary(grid,
                                                xbound=10, ybound=10,
                                                marker=1, quality=34.0)
pg.show(mesh)

tmp = g.Mesh(mesh)
mesh.createH2Mesh(tmp)
tmp = g.Mesh(mesh)
mesh.createP2Mesh(tmp)

for c in mesh.cells():
    if c.marker() == 1:
        c.setMarker(1)
    elif c.marker() == 2:
        c.setMarker(1)
    elif c.marker() == 3:
        c.setMarker(2)
        
print(mesh)
mesh.save('fop-mesh')

#os.system('dcmod -S -s tester.shm -v fop-mesh.bms')
#os.system('dcedit -v -o tester.dat -N -E -u1e-5 -e 1 tester.ohm')

#os.system( 'dcinv -l1 -vvv -S -J -p mesh.bms tester.dat')
os.system('dcinv --localRegularization -f region.control -l1.0 -vvv -S -J -p mesh.bms tester.dat')

