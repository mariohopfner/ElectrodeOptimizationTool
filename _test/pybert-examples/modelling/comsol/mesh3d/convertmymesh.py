# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 11:52:54 2012

@author: Guenther.T
"""

import pygimli as g
import numpy as N

Node = N.loadtxt( 'node.txt' )
Tri  = N.sort( N.loadtxt( 'tri.txt', dtype='int' ), 1 ) # ascending order

# remove duplicate tetrahedra
uidx = N.unique( Tri.dot( N.random.rand(4) ), return_index=True )[1]
Tri = Tri[uidx,]

mesh = g.Mesh( 3 )
for node in Node:
    mesh.createNode( node[0], node[1], node[2] )

for tri in Tri:
    mesh.createTetrahedron( mesh.node( int(tri[0]-1) ), mesh.node( int(tri[1]-1) ) ,
                            mesh.node( int(tri[2]-1) ), mesh.node( int(tri[3]-1) ) )

print(mesh)
mesh.save('mymesh.bms')
mesh.exportVTK( 'mymesh.vtk' )

# extract surface from it
mesh.createNeighbourInfos()
for b in mesh.boundaries() :
    if not( b.leftCell() and b.rightCell() ):
        b.setMarker( 1 )

poly = g.Mesh( 3 )
poly.createMeshByBoundaries( mesh, mesh.findBoundaryByMarker( 1 ) )
poly.exportAsTetgenPolyFile( 'mysurface.poly' )
poly.exportVTK( 'mysurface.vtk' )

# H-refined (H2) mesh
meshH2 = g.Mesh( 3 )
meshH2.createH2Mesh( mesh )
print(meshH2)
meshH2.save( 'mymeshH2.bms' )
# twice H-refined (H3) mesh
meshH3 = g.Mesh( 3 )
meshH3.createH2Mesh( meshH2 )
print(meshH3)
meshH3.save( 'mymeshH3.bms' )
# P-refined (P2) mesh
meshP2 = g.Mesh( 3 )
meshP2.createP2Mesh( mesh )
print(meshP2)
meshP2.save( 'mymeshP2.bms' )
# H-refined and P-refined (H2P2) mesh
meshH2P2 = g.Mesh( 3 )
meshH2P2.createP2Mesh( meshH2 )
print(meshH2P2)
meshH2P2.save( 'mymeshH2P2.bms' )
