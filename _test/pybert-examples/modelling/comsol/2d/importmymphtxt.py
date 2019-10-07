import pylab as P

filename = 'faultzone.mphtxt'
fid = open( filename )
lines = fid.readlines()
fid.close()

P.figure(1)
P.clf()

cols, marks = 'bgrcmykykyk', '...v^<>+xs*h1234'
iobj = 0
ivert, nvert, iedge, nedge,  = 0, 0, 0, 0
for i, line in enumerate(lines):
    if ( line.find( '# number of vertices' ) > 0 ) & ( ivert == 0 ):
        ivert = i
        nvert = int( line.split()[0] )
    if ( line.find( '# number of edges' ) > 0 ) & ( iedge == 0 ):
        iedge = i
        nedge = int( line.split()[0] )

        xv, yv = P.zeros( (nvert,) ), P.zeros( (nvert,) )
        for i in range( nvert ):
            xv[i] = float( lines[i+ivert+3].split()[0] )
            yv[i] = float( lines[i+ivert+3].split()[1] )
        
        E = []
        for i in range( nedge ):
            nums = lines[i+iedge+3].split()[:2]
            E.append( [ int( nums[0] ) - 1, int( nums[1] ) - 1 ] )
        
        ivert, iedge, nvert, nedge = 0, 0, 0, 0
        col = cols[ P.mod( iobj, len(cols) ) ]
        P.plot( xv, yv, col + marks[P.mod( iobj,len(marks))] )
        P.text( P.mean(xv), P.mean(yv), str( iobj ), color=col, va='top' )
        iobj += 1
        for e in E:
            P.plot( xv[e], yv[e], col + '-' )

P.show()
#P.savefig('comsol-input.pdf',bbox_inches='tight')