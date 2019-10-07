#!/usr/bin/env python

import pygimli.meshtools as mt
import pybert as pb

def simulate_data_from_world(world, scheme_file, resistivities):

    # create mesh from world
    mt.exportPLC(world, "_test.poly")
    mesh = mt.createMesh(world, quality=33)

    # pg.show(mesh, data=mesh.cellMarkers(), label='Marker', showMesh=True)
    mesh = mesh.createP2()
    print(mesh)

    data = pb.simulate(mesh, res=[[1,resistivities[0]],[2,resistivities[1]],[3,resistivities[2]]],
                       scheme=pb.load(scheme_file), verbose=True)
    return data