#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    SPHINXME
    
    Example for the basics of all resistivity forward modeling using pygimli.
    
"""

import pygimli as pg
import pybert as pb

"""
Please take care that mkmesh.sh is called once before.
Firstly load the mesh and show mesh size.
"""
mesh = pg.Mesh('mesh/world.bms')
print(mesh)

"""
Initialise one instance f of the finite element dc-geoelectric forward operator
"""
f = pb.DCMultiElectrodeModelling(mesh, True)

"""
Create an empty DataMap instance, i.e., a representation of the collect file.
"""
dMap = pb.DataMap()

"""
Compute potential matrix in dMap and fill also the electrode positions from the mesh.
"""
f.calculate(dMap)

"""
Print electrode positions
"""
for i, el in enumerate(dMap.electrodes()): print((i, el))

"""
You can save the collect file.
"""
dMap.save('numPy.collect')

"""
Load scheme file
"""
shm = pb.DataContainerERT('dipdip.shm')

"""
Apply potentials to scheme yielding resistance
"""
R = dMap.data(shm)
k = f.calcGeometricFactor(shm)
rhoa = R * k
print(('apparent resistivities:', rhoa))

"""
The whole thing is even easier if we integrate the scheme directly
"""
f1 = pb.DCMultiElectrodeModelling(mesh, shm, True)

"""
Create resistivity vector (model) of constant 1.0 and calculate the modeling response for this model
"""
res = pg.RVector(mesh.cellCount(), 1.0)
print(('modeled total field :', f1(res)))

"""
For singularity removal we need a different forward operator but the handling is the same.
The result are the same because of homogeneous resistivity.
"""
f2 = pb.DCSRMultiElectrodeModelling(mesh, shm, True)
print(('modeled with singularity removel:', f2(res)))