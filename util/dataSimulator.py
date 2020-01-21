#!/usr/bin/env python

import numpy as np
import pygimli as pg
import pybert as pb
import pygimli.meshtools as mt


def simulate_data_from_world(world, scheme, resistivities, electrode_spacing, mesh_quality, noiseLevel, noiseAbs, verbose):

    # get ERT manager
    ert = pb.ERTManager()

    # refine mesh at electrode positions
    for pos in scheme.sensorPositions():
        world.createNode(pos)
        world.createNode(pos + pg.RVector3(0, -electrode_spacing/2))

    # create mesh from world
    mesh = mt.createMesh(world, quality=mesh_quality)

    # pg.show(mesh, data=mesh.cellMarkers(), label='Marker', showMesh=True)
    # mesh = mesh.createP2()
    # print(mesh)

    # check if given mesh fits given resistivities
    uniquemarkers = np.unique(np.array(mesh.cellMarkers()), return_inverse=True)
    if len(uniquemarkers[0]) != len(resistivities):
        print("Marker count does not fit given resistivities!")
        return None

    # create resistivity array
    res = []
    i = 1
    for r in resistivities:
        res.append([i,r])
        i = i + 1

    # prepare model
    k = pg.geometricFactor(scheme, 2)
    scheme.markInvalid(pg.isInf(k))
    scheme.removeInvalid()

    # run simulation
    data = ert.simulate(mesh, res=res, scheme=scheme, verbose=verbose, noiseLevel=noiseLevel, noiseAbs=noiseAbs)
    data.markInvalid(data('rhoa') < 0)
    data.removeInvalid();
    return data