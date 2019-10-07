from math import sin, cos, pi
import pylab as P
import pygimli as g
from pygimli.mplviewer import drawModel, drawMeshBoundaries

# load borehole positions and depths from file
xe, ye, de = P.loadtxt('positions.txt',skiprows=1,unpack=True)
nel = len( xe ) #  number of electrodes
elpos = [g.RVector3( xe[i],ye[i],0.) for i in range(nel)]
maxext = max( max(xe)-min(xe), max(xe)-min(xe) ) # maximum extent
pbou, obou =  maxext * 0.2, maxext * 2 # +15% for inversion, 3x for forward

poly = g.Mesh( 2 ) # empty mesh
# outer boundary box (for forward calculation) - mixed
no0 = poly.createNode( min(xe) - obou, min(ye) - obou, 0.)
no1 = poly.createNode( max(xe) + obou, min(ye) - obou, 0.)
no2 = poly.createNode( max(xe) + obou, max(ye) + obou, 0.)
no3 = poly.createNode( min(xe) - obou, max(ye) + obou, 0.)
poly.createEdge( no0, no1, g.MARKER_BOUND_MIXED )
poly.createEdge( no1, no2, g.MARKER_BOUND_MIXED )
poly.createEdge( no2, no3, g.MARKER_BOUND_MIXED )
poly.createEdge( no3, no0, g.MARKER_BOUND_MIXED )
# inner boundary box (for inversion) - natural Neumann conditions
ni0 = poly.createNode( min(xe) - pbou, min(ye) - pbou, 0.)
ni1 = poly.createNode( max(xe) + pbou, min(ye) - pbou, 0.)
ni2 = poly.createNode( max(xe) + pbou, max(ye) + pbou, 0.)
ni3 = poly.createNode( min(xe) - pbou, max(ye) + pbou, 0.)
poly.createEdge( ni0, ni1, g.MARKER_BOUND_HOMOGEN_NEUMANN )
poly.createEdge( ni1, ni2, g.MARKER_BOUND_HOMOGEN_NEUMANN )
poly.createEdge( ni2, ni3, g.MARKER_BOUND_HOMOGEN_NEUMANN )
poly.createEdge( ni3, ni0, g.MARKER_BOUND_HOMOGEN_NEUMANN )

# borehole definitions and auxiliary vector holding nodes
seg, rB = 3, 5. # segments and borehole radius
bpos = [g.RVector3(sin(phi),cos(phi),0.) for phi in P.arange(seg)*2*pi/seg]
# create nodes defining the individual borehole
for elp in elpos: # boreholes
    bn = [] # list of points to connect
    for bp in bpos: # points
        bn.append( poly.createNode( elp + bp*rB ) )
        if len(bn)>1:
            poly.createEdge( bn[-2], bn[-1], 2 )

    poly.createEdge( bn[-1], bn[0], 0 ) # edge back to beginning

# triangulate mesh using triangle algorithm
tri = g.TriangleWrapper( poly ) # wrapper from PLC plus background marker
tri.addRegionMarkerTmp( -1, no0.pos() + g.RVector3( 0.1, 0.1, 0. ), 0. )
# set options (plc,zero counting,no ele file, attribute,quality)
tri.setSwitches( "-pzeAq34.5" )
mesh2 = g.Mesh( 2 ) # better would be mesh2 = tri.generate()
tri.generate( mesh2 )
mesh2.smooth( True, False, 0, 5)
print("2D", mesh2)

# show mesh markers and discretization
fig=P.figure(2)
fig.clf()
ax=fig.add_subplot(111)
drawModel( ax, mesh2, mesh2.cellMarker(), linear=True )#,showCbar=False )
drawMeshBoundaries( ax, mesh2, False )
P.xlim( ( min(xe) - pbou*1.3, max(xe) + pbou*1.3 ) )
P.ylim( ( min(ye) - pbou*1.3, max(ye) + pbou*1.3 ) )

# create vertical discretization (depth, layers, fine part, )
maxdep, nl, dz0 = 230, 20, 2.*P.pi/(seg+0.5)*rB # appr. equal sides
z = -g.increasingRange( dz0, maxdep, nl) # vector of nl points from 0,dz,...,maxdep
print(z)

# extrude 2D mesh into 3D, inner bounds from edges, top=Neumann, bottom=Mixed
mesh3 = g.createMesh3D( mesh2, z, g.MARKER_BOUND_HOMOGEN_NEUMANN, g.MARKER_BOUND_MIXED )
print(mesh3)
jlist = list(range( mesh3.cellCount())) # list of all cell numbers
for i in range( nel ): # all electrodes
    for j, mid in enumerate( mesh3.cellCenter() ): # all cells
        diq = ( xe[i] - mid.x() )**2 + ( ye[i] - mid.y() )**2 # squared distance
        if diq < rB**2 and abs( mid.z() ) < de[i]: #inside radius and < depth
            jlist.remove(j) #apparently inside borehole

# copy list into standard vector of ints
idx = g.stdVectorI()
for jj in jlist: idx.append(jj)
# generate new mesh and generate from index vector
mesh4 = g.Mesh( 3 )
mesh4.createMeshByCellIdx( mesh3, idx )

# set boundary marker according to their cell centers
bx = P.array([bb.center().x() for bb in mesh4.boundaries()])
by = P.array([bb.center().y() for bb in mesh4.boundaries()])
bz = P.array([-bb.center().z() for bb in mesh4.boundaries()])
for i in range( nel ):
    diq = ( bx-xe[i] )**2 + ( by-ye[i] )**2
    for ai in P.nonzero( ( diq < rB**2 ) & ( bz < de[i] ) )[0]:
        mesh4.boundary( int(ai) ).setMarker( -10000 - i ) # CEM electrode no. i
        
# export the resulting meshes and boundaries
mesh4.exportBoundaryVTU('bounds.vtu') # only boundaries for checking
mesh4.exportVTK( 'prisMesh.vtk' )     # prism mesh
mesh4.save( 'prisMesh.bms' )          # mesh to calculate with
