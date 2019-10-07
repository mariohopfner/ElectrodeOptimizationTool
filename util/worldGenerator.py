#!/usr/bin/env python

import pygimli.meshtools as mt
import pybert as pb


'''
Functions that creates a PyGimli world with given parameters
    :parameter
        scheme_file        - name of the scheme file
        x                  - length of world in x dimension
        y                  - length of world in y dimension
        layers             - depths of subsurface-splitting horizons
'''
def generate_simple_layered_world(scheme_file, x=100, y=100, layers=None):
    if layers is None:
        layers = []

    # if first layer is the surface layer, remove it
    if len(layers) > 0 and layers[0] == 0:
        layers.pop(0)

    # create world
    world = mt.createWorld(start=[0,0], end=[x,-y], layers=layers)

    # load given scheme file
    scheme = pb.load(scheme_file)

    # add electrodes defined in scheme file
    for s in scheme.sensors():
        world.createNode(s + [0.0, -0.2])

    return world
