#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pygimli as g
from pygimli.mplviewer import setOutputStyle

# default one axis
setOutputStyle( xScale=1.0, yScale=1.0 / (2*1.618), scale=2 )
# default one axis
#setOutputStyle( xScale=1.0, scale=2, fontsize=9, usetex = True)

import pylab as P

def showEffect( a, cem, pem, idx = None, alpha = 1, title = '' ):
    
    if idx is None:
        idx = g.find( g.abs( cem('r') ) > 0.0 )
    
    
    #print "nData ", len( kIdx )
    #e = ( cem('r')(kIdx) / pem('r')(kIdx) - 1.0 ) * 100.0;
        
    #kfail = g.find( g.abs(e) > 10 )
    #P.hist( k(kfail ), 100 )
    #P.show()
    e = ( cem('r')( idx ) / pem('r')( idx ) - 1.0 ) * 100.0;
    estd = g.stdDev( e )
    emi = min( e )
    ema = max( e )
    
    ep = ( pem('r')( idx ) / cem('r')( idx ) - 1.0 ) * 100.0;
    epstd = g.stdDev( ep )
    ep1 = float( len( g.find( g.abs( ep ) < 1 ) ) ) / len( ep )* 100
    ep10 = float( len( g.find( g.abs( ep ) > 10 ) ) ) / len( ep )* 100
    epmi = min( ep )
    epma = max( ep )

    print("%.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f & %.1f" %(emi,ema,estd, epmi,epma,epstd, ep1, ep10))
    print("lower than Zero:", len( g.find( cem('r')( idx ) / pem('r')( idx ) < 0.0 ) ))
    #, '&', ema, '&', stdE, '&', e1, '&', e10, '&', stdEP, '&', epmi, '&', epma, '&', ep1, '&', ep10
    
    
    label = title + ' std = ' + ('%.1f' % estd) + "$\%$"
    #, $1< 1\%:$ %.1f $ 10:$ %.1f" % (title, estd, e1, e10 )
    #print label
    #print "%s std: %.1f, min: %.1f max: %.1f" % (title, stdEP, epmi, epma )
    #print "lower 1%", e1 "%", "larger 10%", e10, "%"
          
    bins = list(range(-49, 50, 1)); bins.insert( 0, -1000 ); bins.append( 1000 )

    a.hist( e, bins = bins, log = True, alpha = alpha, color = (0.5, 0.5, 0.5) )

    a.text( -45, 3000, label )

    a.set_xlim( [-50, 50 ] )
    a.set_ylim( [0.5, 10000 ] )
    a.set_xlabel("(Electrode effect $ - 1 )\cdot 100\%$ ")
    
    #a.grid()
    a.set_ylabel("Frequency")

    #xt = [-50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50]
    xt = [-50, -30, -10, 0, 10, 30, 50]
    xtl = [-50, -30, -12, 1.2, 12, 30, 50]
    
    xticks=[]
    xtickLabels=[]
    for i in [1, 10, 100, 1000 ]:
        a.semilogy( a.get_xlim(), [ i, i ], linestyle='dotted', color = 'black')
        
    for i, l in enumerate( xt ):
        a.plot( [ l, l ], a.get_ylim(), linestyle='dotted', color = 'black')
        
        tick = l
        xticks.append( xtl[ i ] ) 
    
        if l < -40:
            xtickLabels.append( '    $<' + str( tick) + '\\%$' )
        elif l > 40:
            xtickLabels.append( '$>' + str( tick) + '\\%$' )
        elif tick > 0:
            xtickLabels.append( '$\\phantom{00}' + str( tick) + '\\%$' )
        elif tick > 10:
            xtickLabels.append( '$~~~' + str( tick) + '\\%$' )
        else:
            xtickLabels.append( '$' + str( tick) + '\\%$' )
    
    a.set_xticks( xticks )
    a.set_xticklabels( xtickLabels )
    
        
# def showEffect()dataE1e6-1.11.ohm  docalc.sh                 elecs-tank-log-effect.pdf  shresults.py~

def compareAll( quality ):
    cem1 = g.DataContainer( "dataE1e6" + str(quality) + ".ohm" )
    cem2 = g.DataContainer( "dataE1e-6" + str(quality) + ".ohm" )
    pem0 = g.DataContainer( "data0.ohm" )
    pem1 = g.DataContainer( "data1.ohm" )
#    pem2 = g.DataContainer( "dataP2.ohm" )
#    pem3 = g.DataContainer( "dataP3.ohm" )
#    pem15 = g.DataContainer( "dataP1.5.ohm" )

    #fig1 = P.figure(1)
    #a = fig1.add_subplot( 1, 1, 1 )
    #showEffect( a, cem1, cem2, title = 'CEM($z_l=10^{6}\\Omega$m$) / $CEM$(z_l=10^{-6}\\Omega m)$' )
    #P.savefig( "cem-cem_effect-cem_mesh-p-q-"+str(quality)+".pdf" )
    
    k = 1./cem1('r');
    idx = g.find( g.abs( k ) < 1000 )
    
    print(100.-float(len( idx )) / len(k) * 100.)
    fig2 = P.figure(2)
    a = fig2.add_subplot( 5, 2, 1 )
    showEffect( a, cem1, pem0, idx, title = 'CEM($z_l=10^{6}\\Omega$m$) / $PEM(0\\%)' )
    
    a = fig2.add_subplot( 5, 2, 2 )
    #showEffect( a, cem2, pem0, title = 'CEM($z_l=10^{-6}\\Omega$m$) / $PEM(0\\%)' )

    a = fig2.add_subplot( 5, 2, 3 )
    showEffect( a, cem1, pem1, idx,  title = 'CEM($z_l=10^{6}\\Omega$m$) / $PEM(33\\%)' )

    a = fig2.add_subplot( 5, 2, 4 )
    #showEffect( a, cem2, pem1, title = 'CEM($z_l=10^{-6}\\Omega$m$) / $PEM(33\\%)' )

    a = fig2.add_subplot( 5, 2, 5 )
#    showEffect( a, cem1, pem15,  idx, title = 'CEM($z_l=10^{6}\\Omega$m$) / $PEM(50\\%)' )

    a = fig2.add_subplot( 5, 2, 6 )
    #showEffect( a, cem2, pem15, title = 'CEM($z_l=10^{-6}\\Omega$m$) / $PEM(50\\%)' )

    a = fig2.add_subplot( 5, 2, 7 )
#    showEffect( a, cem1, pem2,  idx, title = 'CEM($z_l=10^{6}\\Omega$m$) / $PEM(66\\%)' )

    a = fig2.add_subplot( 5, 2, 8 )
    #showEffect( a, cem2, pem2, title = 'CEM($z_l=10^{-6}\\Omega$m$) / $PEM(66\\%)' )

    a = fig2.add_subplot( 5, 2, 9 )
#    showEffect( a, cem1, pem3,  idx, title = 'CEM($z_l=10^{6}\\Omega$m$) / $PEM(100\\%)' )

    a = fig2.add_subplot( 5, 2, 10 )
    #showEffect( a, cem2, pem3, title = 'CEM($z_l=10^{-6}\\Omega$m$) / $PEM(100\\%)' )

    P.savefig( "cem-pem_effect-cem_mesh-p-q-"+str(quality)+".pdf" )
# def compareAll


fig = P.figure(1)

cem1 = g.DataContainer( "dataE1e6"  + ".ohm" )
cem2 = g.DataContainer( "dataE1e-6" + ".ohm" )
pem0 = g.DataContainer( "data0.ohm" )

k = 1./cem1('r')
idx = g.find( g.abs( k ) < 1000 )

#a = fig.add_subplot( 1, 2, 1 )
#showEffect( a, cem1, pem0, title = 'All data, ' )
#a.set_xlabel( 'Electrode effect: $(\\text{CEM}/\\text{PEM}-1)\cdot 100\%$' )
##a.set_xlabel( 'Electrode effect: $\\left(\\dfrac{\\text{CEM} (z_l=10^{6}\\Omega \\text{m}^2)}{\\text{PEM}}-1\\right) \cdot 100$' )
#a = fig.add_subplot( 1, 2, 2 )
#showEffect( a, cem1, pem0, idx, title = 'Filtered data $(k < 1000)$, ' )
#a.set_xlabel( 'Electrode effect: $(\\text{CEM}/\\text{PEM}-1)\cdot 100\%$' )
##a.set_xlabel( 'Electrode effect: $\\left(\\dfrac{\\text{CEM} (z_l=10^{6}\\Omega \\text{m}^2)}{\\text{PEM}}-1\\right) \cdot 100$' )

a = fig.add_subplot( 1, 2, 1 )
showEffect( a, pem0, cem1, title = 'All data, ' )
a.set_xlabel( 'Point source error: $(u_\\text{PEM}/u_\\text{CEM}-1)\cdot 100\%$' )
#a.set_xlabel( 'Electrode effect: $\\left(\\dfrac{\\text{CEM} (z_l=10^{6}\\Omega \\text{m}^2)}{\\text{PEM}}-1\\right) \cdot 100$' )
#    a.yaxis.labelpad = -5
a = fig.add_subplot( 1, 2, 2 )
showEffect( a, pem0, cem1, idx, title = 'Filtered data $(|k| < 1000)$, ' )
a.set_xlabel( 'Point source error: $(u_\\text{PEM}/u_\\text{CEM}-1)\cdot 100\%$' )
#    a.yaxis.labelpad = -5

#a = fig.add_subplot( 2, 2, 3 )
#showEffect( a, cem2, pem0, title = '(CEM($z_l=10^{-6}\\Omega$m$) / $PEM$-1)100$' )
#a = fig.add_subplot( 2, 2, 4 )
#showEffect( a, cem2, pem0, idx, title = '(CEM($z_l=10^{-6}\\Omega$m$) / $PEM$ -1) 100 k < 1000$' )
    
#P.plot( es )

fig.canvas.draw()
    
fig.subplots_adjust( left = 0.065, bottom=0.18, right = 0.97, top = 0.96
                    , wspace=0.2, hspace=0.3 ) 
                    
P.savefig( "elecs-tank-log-effect.pdf", bbox_inches='tight' )
#os.system( 'pdf2pdfBB "elecs-tank-log-effect.pdf"')

P.show()
