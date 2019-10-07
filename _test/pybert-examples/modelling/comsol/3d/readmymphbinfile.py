import pylab as P

#filename = 'deposit.mphtxt'
filename = 'layer2block.mphtxt'
fid = open( filename )
lines = fid.readlines()
fid.close()

ivert, nvert, iedge, nedge, ipe, npe, nface, iface  = 0, 0, 0, 0, 0, 0, 0, 0
for i, line in enumerate(lines):
    if ( line.find( '# number of vertices' ) > 0 ) & ( ivert == 0 ):
        ivert = i
        nvert = int( line.split()[0] )
    if ( line.find( '# number of edges' ) > 0 ):
        iedge = i
        nedge = int( line.split()[0] )
    if ( line.find( '# number of parameter edges' ) > 0 ):
        ipe = i
        npe = int( line.split()[0] )
    if ( line.find( '# number of faces' ) > 0 ):
        iface = i
        nface = int( line.split()[0] )
            
xv, yv, zv = P.zeros( (nvert,) ), P.zeros( (nvert,) ), P.zeros( (nvert,) )
for i in range( nvert ):
    lini = lines[i+ivert+3].split()
    xv[i] = float( lini[0] )
    yv[i] = float( lini[1] )
    zv[i] = float( lini[2] )

#P.vstack((xv.round(2),yv,zv.round(3))).T

edge = P.zeros( (nedge,2), dtype=int )
me = P.zeros( (nedge,), dtype=int )
for i in range( nedge ):
    nums = lines[i+iedge+3].split()
    edge[i,0] = int( nums[0] ) - 1
    edge[i,1] = int( nums[1] ) - 1
    me[i] = int( nums[5] )

pe = P.zeros( (npe,2), dtype=int )
for i in range( npe ):
    nums = lines[i+ipe+3].split()
    pe[i,0] = int( nums[0] ) - 1
    pe[i,1] = int( nums[8] ) - 1

face = []
for i in range( nface ):
    face.append( int( lines[i+iface+3].split()[2] ) )

#pe[ pe[:,1] == abs(face[0]), 0 ]
for facei in face:
    print("Face ")
    print(edge[ pe[ pe[:,1] == abs( facei ), 0 ], :].T)