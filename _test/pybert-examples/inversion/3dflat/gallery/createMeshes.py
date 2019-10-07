#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import numpy as np

import pygimli as pg
from pygimli.viewer import showMesh
from pygimli.meshtools import appendTriangleBoundary

import pybert as pb


def createMixMesh(verbose=True):
    """
    """
    xdim = [0, 20, 2.5 ]
    ydim = [0, 32.5, 2.5 ]
    dxy = [ 2.5, 2.5 ]
    paraBoundary = 2.5
    boundary = 50
    depth = 10

    grid = pg.createGrid(x=np.arange(xdim[0]-paraBoundary, xdim[1]+paraBoundary, xdim[2]*1.0),
                       y=np.arange(ydim[0]-paraBoundary, ydim[1]+paraBoundary, ydim[2]*1.0))

    for b in grid.boundaries():
        b.setMarker(1)

    for c in grid.cells():
        c.setMarker(2)

    grid.translate((0.0, -grid.ymax() - boundary))

    mesh2 = pg.meshtools.appendTriangleBoundary(grid,
                                                xbound=boundary,
                                                ybound= boundary,
                                                quality=30,
                                                marker=1, isSubSurface=True)

    mesh2.smooth(True, False, 1, 2)
    mesh2.translate((0.0, -grid.ymax() + ydim[1]))

    for b in mesh2.boundaries():
        if b.marker() < 0:
            b.setMarker(pg.MARKER_BOUND_MIXED)

    #showMesh(mesh2)

    mesh3 = pg.createMesh3D(mesh2,
                            -pg.cat(pg.increasingRange(2.5/2., 10., 6),
                                    pg.increasingRange(2.5, boundary, 10) + 12.5),
                            pg.MARKER_BOUND_HOMOGEN_NEUMANN,
                            pg.MARKER_BOUND_MIXED)

    for c in mesh3.cells():
        if c.marker() == 2:
            if c.center()[2] < -depth: c.setMarker(1)

    return mesh3

createMixMesh().save("mesh/mesh")
