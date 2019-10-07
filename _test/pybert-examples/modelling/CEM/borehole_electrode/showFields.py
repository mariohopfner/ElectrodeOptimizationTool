# -*- coding: utf-8 -*-
#/usr/bin/env python
'''
'''
import os

import pygimli as g
import pygimli.utils
import pygimli.misc
from pygimli.mplviewer import *

from pygimli.mplviewer import createLogLevs, setOutputStyle, drawSelectedMeshBoundariesShadow

setOutputStyle( xScale = 1.0, yScale = 0.25, fontsize=7, scale = 2, usetex = True )

import pylab as P
import matplotlib as mpl
import numpy as np

def drawPotential( axes, mesh, u, x=[-10.0, 50.0], z=[-50.0, 0.0]
                    , dx=1, nLevs = 20, title = None, verbose = False, maskZero = False ):
    '''
        draw dc potential
    '''
    
    import numpy as np
    swatch = g.Stopwatch( True )
    if ( verbose ):
        print("start interpolation:", swatch.duration( True ))
        
    xg = createLinLevs( x[ 0 ], x[ 1 ], int( ( x[1] - x[0] ) / dx ) )
    yg = createLinLevs( z[ 0 ], z[ 1 ], int( ( z[1] - z[0] ) / dx ) )
    X,Y = np.meshgrid( xg,yg)
    
    uI = g.interpolate( mesh, u
                    , g.ListToRVector( list( X.flat ) )
                    , g.RVector( len( Y.flat ), 0.0 )
                    , g.ListToRVector( list( Y.flat ) ), verbose )
    
    if ( verbose ):
        print("interpolation:", swatch.duration( True ))

    zi = np.array( uI )
    if maskZero:
        zi = np.ma.masked_where( zi <= 0.0, zi )
    Z = zi.reshape( X.shape )
    gci = axes.contourf( X, Y, Z, nLevs )
    axes.contour( X, Y, Z, nLevs, colors = 'white', linewidths = 0.8 )
    axes.set_aspect('equal')
    
    axes.set_xlim( x )
    axes.set_ylim( z )
    
    axes.set_ylabel( 'Depth [m]')
    axes.set_xlabel( '$x$ [m]')
    if title is not None:
        axes.set_title( title )
    
    if ( verbose ):
        print("time:", swatch.duration( True ))
        
    print("fixing 'Depth' to be positive values")
    ticks = axes.yaxis.get_majorticklocs()
    tickLabels=[]
    for t in ticks:
        tickLabels.append( str( int( abs( t ) ) ) )
        axes.set_yticklabels( tickLabels )
        
    return gci
# def drawPotential

def intersectionLines( boundaries, plane ):
    lines = []

    for b in boundaries:
        ps = []
        for i, n in enumerate( b.shape().nodes() ):
            line = g.Line( n.pos(), b.shape().node( (i+1)%b.shape().nodeCount() ).pos() )
            p = plane.intersect( line, 1e-8, True )
            if p.valid():
                ps.append( p )
        
        if len( ps ) == 2:
            lines.append( list(zip( [ ps[0].x(), ps[1].x() ],
                               [ ps[0].z(), ps[1].z() ] )) )
    return lines
# def intersectionLines
    
g.checkAndFixLocaleDecimal_point( True )

dn = g.DataContainer( '21cpp-node.dat' )
dz = g.DataContainer( '21cpp-1e-6.dat' )
dZ = g.DataContainer( '21cpp-1e6.dat' )

idx = g.find( dn('a') == 0 )

fig = P.figure()
a4 = fig.add_subplot( 1, 3, 1 )
a5 = fig.add_subplot( 1, 3, 2 )

a = fig.add_subplot( 1, 3, 3)


a.plot( np.arange(1, len(idx)+1, 1)*10, dn('rhoa')( idx ), label = 'Point source' )
a.plot( np.arange(1, len(idx)+1, 1)*10, dz('rhoa')( idx ), label = 'Borehole' )
#a.plot( np.arange(1, len(idx)+1, 1)*10, dZ('rhoa')( idx ), label = '$z = 10^4$' )
a.set_ylabel('Apparent resistivity $\Omega$m')
a.set_xlabel('Pole-Dipole separation [m]')

legend = a.legend( loc='upper right' )
for t in legend.get_texts():
    t.set_fontsize('medium')
#legend.draw_frame(0)

a.set_xlim( 10, len(idx)*10)
a.set_xticks( np.arange(1, len(idx)+1, 2)*10 )
a.grid(True)


#a6 = fig.add_subplot( 2, 2, 6 )

windowX = [ -100.0, 200.0 ]
windowZ = [ -200.0, 0.0 ]
dx = 0.25

swatch = g.Stopwatch( True )

mesh4 = g.Mesh( 'mesh/world' )
pot4 = g.RMatrix( 'pot/num-node.bmat')
mesh5 = g.Mesh( 'mesh/world-cem' )
pot5  = g.RMatrix( 'pot/num-1e-4.bmat')

print("loaded:", swatch.duration( True ))
lines = intersectionLines( mesh4.findBoundaryByMarker( -9999 ), g.Plane( g.RVector3( 0.0, 1.0, 0.0 ), 0.0 ) )
print("found intersection", swatch.duration( True ))

gci = drawPotential( a4, mesh4, pygimli.utils.logDropTol( pot4[ 0 ] , 1e-3 ), title = "Point source"
                , x = windowX, z = windowZ, dx = dx, nLevs = 20, maskZero = True
                , verbose = True )

lineCollectiona4 = mpl.collections.LineCollection( lines, color = ( 0.0, 0.0, 0.0, 1.0 ) )
a4.add_collection( lineCollectiona4 )
gci.set_clim(0.1, 3 )

print("draw a4", swatch.duration( True ))
gci = drawPotential( a5, mesh5, pygimli.utils.logDropTol( pot5[ 0 ], 1e-3 ), title = "Borehole (CEM with $z_l=10^{-4}\\Omega$\,m)"
                , x = windowX, z = windowZ, dx = dx, nLevs = 10, maskZero = True 
                , verbose = True )
lineCollectiona5 = mpl.collections.LineCollection( lines, color = ( 0.0, 0.0, 0.0, 1.0 ) )
a5.add_collection( lineCollectiona5 )
gci.set_clim(0.1, 3 )

for i in createLinLevs( 200/10, 200, 10 ):
    x,y = g.misc.streamline( mesh4, pot4[0], g.RVector3( 200, 0.0, -i ), 0.011, maxSteps=5000)
    a4.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )
    x,y = g.misc.streamline( mesh4, pot4[0], g.RVector3( -100, 0.0, -i ), 0.011, maxSteps=5000)
    a4.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )
    
    x,y = g.misc.streamline( mesh5, pot5[0], g.RVector3( 200, 0.0, -i ), 0.005, maxSteps=5000)
    a5.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )
    x,y = g.misc.streamline( mesh5, pot5[0], g.RVector3( -100, 0.0, -i ), 0.005, maxSteps=5000)
    a5.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )
    
for i in createLinLevs( -100+200/10, 200-200/10, 15 ):
    x,y = g.misc.streamline( mesh4, pot4[0], g.RVector3( i, 0.0, -200 ), 0.011, maxSteps=5000)
    a4.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )
    x,y = g.misc.streamline( mesh5, pot5[0], g.RVector3( i, 0.0, -200 ), 0.011, maxSteps=5000)
    a5.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )

    
for i in createLinLevs( 65, 120, 8 ):
    x,y = g.misc.streamline( mesh5, pot5[0], g.RVector3( 0.2, 0.0, -i ), 0.005, maxSteps=5000)
    a5.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )

for i in createLinLevs( -5, 38, 8 ):
    x,y = g.misc.streamline( mesh4, pot4[0], g.RVector3( i, 0.0, -60 ), 0.005, maxSteps=5000)
    a4.plot( x,y, color = 'black', linewidth = 0.6, linestyle = 'solid' )

a4.set_xlim( windowX )
a4.set_ylim( windowZ )
a5.set_xlim( windowX )
a5.set_ylim( windowZ )
a4.title.set_y(1.015)
fig.show()
fig.canvas.draw()

fig.subplots_adjust( left = 0.055, right = 0.984, top = 0.989, bottom=0.065, wspace=0.25) # pad a little

a.set_position( a.get_position().expanded( 1.0, 0.77) )

P.savefig( "elecs-borehole.pdf" )
#os.system( "pdf2pdfBB elecs-borehole.pdf" )

#P.show()