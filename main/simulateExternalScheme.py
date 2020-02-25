#!/usr/bin/env python

import datetime
import os

import numpy as np

import pygimli as pg
import pygimli.meshtools as mt
import pybert as pb

from util.InversionConfiguration import InversionConfiguration
import util.worldGenerator as wg
import util.schemeUtil as su

# use inversion config
config = InversionConfiguration(general_bert_verbose=True,
                                world_x=200, world_y=100, world_resistivities=[1000,50], world_gen='incl',
                                world_layers=[], world_angle=0,
                                world_inclusion_start=[20,-20], world_inclusion_dim=[50,30],
                                sim_mesh_quality=34, sim_noise_level=0.1, sim_noise_abs=1e-6,
                                inv_lambda=50, inv_dx=0.3, inv_max_cell_area=30,
                                finv_max_iterations=5, finv_spacing=5, finv_base_configs=['dd'],
                                finv_add_configs=['wa', 'wb', 'pp', 'pd', 'slm', 'hw', 'gr'])

# create folder
start_time = datetime.datetime.now()
folder = "../inversion_results/job-%d%d%d-%d.%d.%d-external/" \
 % (start_time.year,start_time.month,start_time.day,start_time.hour,start_time.minute,start_time.second)
os.makedirs(folder + "tmp/")

# create world
if config.world_gen == "lay":
    world = wg.generate_dipped_layered_world(
        [config.world_x, config.world_y], config.world_layers, config.world_angle)

if config.world_gen == "incl":
    world = wg.generate_hom_world_with_inclusion(
        [config.world_x, config.world_y],
        config.world_inclusion_start, config.world_inclusion_dim)

# create electrodes
electrode_count = np.ceil(config.world_x / config.finv_spacing) + 1
electrodes = pg.utils.grange(start=0, end=config.world_x, n=electrode_count)

# create scheme
scheme = pb.load('extScheme.shm')

# create mesh
spacing = np.floor(len(config.world_x/electrodes))
for pos in scheme.sensorPositions():
    world.createNode(pos)
    world.createNode(pos + pg.RVector3(0, -spacing / 2))

# create mesh from world
mesh = mt.createMesh(world, quality=config.sim_mesh_quality)

# create res array
res = []
i = 1
for r in config.world_resistivities:
    res.append([i, r])
    i = i + 1

# simulate
print("###SIMULATE###")
ert = pb.ERTManager()
syndata = ert.simulate(mesh, res=res, scheme=scheme,
                           verbose=config.general_bert_verbose, noiseLevel=config.sim_noise_level,
                           noiseAbs=config.sim_noise_abs)
syndata.markInvalid(syndata('rhoa') < 0)
syndata.removeInvalid()
syndata.save(folder + 'syndata.dat')

# invert
print("###INVERT###")
ert = pb.ERTManager()
inv = ert.invert(syndata, paraDX=config.inv_dx, maxCellArea=config.inv_max_cell_area,
                 lam=config.inv_lambda, verbose=config.general_bert_verbose)
ert.saveResult(folder)


end_time = datetime.datetime.now()
print(str(start_time))
print(str(end_time))