Example Borehole electrodes with prismatic mesh

This example was the first practical application of CEM to the field-scale, documented by Ronczka et al. (2015). Long electrodes, i.e. boreholes, can be modelled with CEM after Rücker&Günther (2011).
See other examples on how to model CEM electrodes in general.
However the unstructured meshes are not suited for sensitivity analysis (very fine vs. coarse cells).
Furthermore, to model 1D resistivity distribution as a rising salt-water layer, remeshing and splitting boreholes at the boundary are necessary.
Therefore vertical prisms (available in BERT2.-beta21) seem to be appropriate choices for 1d discretization and regioning purposes.
Since long electrodes do not have a constant resistivity in their neighborhood, singularity removal cannot efficiently be employed.

We use Python and the pygimli library for doing the mesh generation (mkmesh.py) and pybert for doing the computations (docalc.py).
The building of the 3D mesh consists of building a 2D triangle mesh and extruding it to depth followed by cell deletion and boundary marking.
After reading the electrode positions from a file we create a big box by adding 4 points and 4 edges.

    poly = g.Mesh( 2 ) # empty mesh with certain boundary around electrodes
    no0 = poly.createNode( min(xe) - obou, min(ye) - obou, 0.)
    no1 = poly.createNode( max(xe) + obou, min(ye) - obou, 0.)
    no2 = poly.createNode( max(xe) + obou, max(ye) + obou, 0.)
    no3 = poly.createNode( min(xe) - obou, max(ye) + obou, 0.)
    poly.createEdge( no0, no1, g.MARKER_BOUND_MIXED )
    poly.createEdge( no1, no2, g.MARKER_BOUND_MIXED )
    poly.createEdge( no2, no3, g.MARKER_BOUND_MIXED )
    poly.createEdge( no3, no0, g.MARKER_BOUND_MIXED )

We do the same with an inner box for later computations as in inversion.
The we insert a regular polygon around each of the electrode positions.
    for elp in elpos: # boreholes
        bn = [] # list of points to connect
        for bp in bpos: # points
            bn.append( poly.createNode( elp + bp*rB ) )
            if len(bn)>1:
                poly.createEdge( bn[-2], bn[-1], 2 )

        poly.createEdge( bn[-1], bn[0], 0 ) # edge back to beginning

The mesh is now triangulated after setting a region marker in the background to distinguis it from the interior.

    tri = g.TriangleWrapper( poly ) # wrapper from PLC plus background marker
    tri.addRegionMarkerTmp( -1, no0.pos() + g.RVector3( 0.1, 0.1, 0. ), 0. )
    tri.setSwitches( "-pzeAq34.5" ) # plc,zero counting,no ele file, attribute,quality
    mesh2 = tri.generate()

We create a z vector with increasing layer thickness and extrude the mesh into 3D.

    z = -g.increasingRange( dz0, maxdep, nl) # vector of nl points from 0,dz,...,maxdep
    mesh3 = g.createMesh3D( mesh2, z, g.MARKER_BOUND_HOMOGEN_NEUMANN, g.MARKER_BOUND_MIXED )

After it we have to remove the cells inside the boreholes (above their maximum depth).

    jlist = range( mesh3.cellCount() ) # list of all cell numbers
    for i in range( nel ): # all electrodes
        for j, mid in enumerate( mesh3.cellCenter() ): # all cells
            diq = ( xe[i] - mid.x() )**2 + ( ye[i] - mid.y() )**2 # squared distance
            if diq < rB**2 and abs( mid.z() ) < de[i]: #inside radius and < depth
                jlist.remove(j) #apparently inside borehole

    idx = g.stdVectorI()
    for jj in jlist: idx.append(jj)
    mesh4 = g.Mesh( 3 )
    mesh4.createMeshByCellIdx( mesh3, idx )

Finally we have to find the faces inside the electrode holes and mark them with the CEM markers.
for i in range( nel ):
    diq = ( bx-xe[i] )**2 + ( by-ye[i] )**2
    for ai in P.nonzero( ( diq < rB**2 ) & ( bz < de[i] ) )[0]:
        mesh4.boundary( int(ai) ).setMarker( -10000 - i ) # CEM electrode no. i

The mesh can then be saved and exported in vtk to see the mesh in Paraview.
Export of the boundaries into a VTU helps to check that the CEM markers are set appropriately.

References:
Rücker, C. & Günther, T. (2011) The simulation of finite ERT electrodes using the complete electrode model. Geophysics, 76, F227.
Ronczka,M.,Voss,T.&Günther,T.(2015):Cost-efficient imaging and monitoring of saltwater in a shallow aquifer by using long-electrode ERT. Journal of Applied Geophysics, 122, 202-209, doi:10.1016/j.jappgeo.2015.08.014.