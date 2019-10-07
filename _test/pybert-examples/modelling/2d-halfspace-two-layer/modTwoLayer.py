#!/usr/bin/env python
import numpy as np

import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics.ert import VESModelling

import pybert as pb

scheme = pb.load('wa24.shm')

### 2D FEM
plc = mt.createWorld(start=[-200, -100], end=[200, 0], layers=[-5], area=[5.0, 500])

for s in scheme.sensors():
    plc.createNode(s + [0.0, -0.2])

mt.exportPLC(plc, "_test.poly")
mesh = mt.createMesh(plc, quality=33)

# pg.show(mesh, data=mesh.cellMarkers(), label='Marker', showMesh=True)
mesh = mesh.createP2()
print(mesh)

data = pb.simulate(mesh, res=[[1, 100.0], [2, 1.0]], 
                   scheme=scheme, verbose=True)

### 1D VES
x = pg.x(scheme)
ab2 = (x[scheme('b')] - x[scheme('a')])/2
mn2 = (x[scheme('n')] - x[scheme('m')])/2
ves = VESModelling(ab2=ab2, mn2=mn2)


### Plot results
fig, ax = pg.plt.subplots(1,1)
ax.plot(ab2, data('rhoa'), '-o', label='BERT 2D (FEM)')
ax.plot(ab2, ves.response([5.0, 100.0, 1.0]), '-x', label='BERT 1D (VES)')
ax.set_xlabel('ab/2 (m)')
ax.set_ylabel('Apparent resistivity ($\Omega$m)')
ax.grid(1)
ax.legend()

pg.wait()

