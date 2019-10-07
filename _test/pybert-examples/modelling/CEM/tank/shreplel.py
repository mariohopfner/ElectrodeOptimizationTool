# -*- coding: utf-8 -*-
"""
Created on Fri Jul 02 14:33:19 2010

@author: Guenther.T
"""

import pygimli as g
import numpy as N

dx = [ 0, 1]#, 1.5, 2, 3 ]
STD = N.zeros( len(dx) )
for i in range( len( dx ) ):
    file="effect" + str(dx[i]) + ".data"
    
    data = g.DataContainer(file)
    r=data("rhoa")
    e=r*100. - 100.
    k=data("k")
    print(data)
    print(min(e),max(e),N.std(e))
    e1 = e(g.find(g.abs(k)<1000))
    print(min(e1),max(e1),N.std(e1),N.median(e1))
