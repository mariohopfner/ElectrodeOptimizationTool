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
                                    world_inclusion_start=[80,-20], world_inclusion_dim=[20,10],
                                    sim_mesh_quality=34, sim_noise_level=0.2, sim_noise_abs=1e-6,
                                    inv_lambda=50, inv_para_dx=0.1, inv_max_cell_area=10,
                                    finv_max_iterations=8, finv_spacing=2, finv_base_configs=['dd'],
                                    finv_add_configs=['wa', 'wb', 'pp', 'pd', 'slm', 'hw', 'gr'],
                                    finv_gradient_weight=0)

# create folder
start_time = datetime.datetime.now()
folder = "../inversion_results/job-%d%d%d-%d.%d.%d-fullinv/" \
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
schemes = ['wa', 'wb', 'pp', 'pd', 'dd', 'slm', 'hw', 'gr']
electrode_counts = [np.ceil(config.world_x / config.finv_spacing) + 1]
comp_electrodes = [pg.utils.grange(start=0, end=config.world_x, n=electrode_counts[0])]
j = 0
while np.floor((electrode_counts[j]-1)/2) == (electrode_counts[j]-1)/2:
    electrode_counts.append((electrode_counts[j]-1)/2+1)
    j = j + 1
    comp_electrodes.append(pg.utils.grange(start=0, end=config.world_x, n=electrode_counts[j]))
comp_scheme = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[0])
for j in range(1,len(comp_electrodes)):
    scheme_tmp = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[0])
    comp_scheme = su.merge_schemes(comp_scheme, scheme_tmp, folder + "tmp/")

for i in range(1,len(schemes)-1):
    scheme_tmp = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[i])
    for j in range(1, len(comp_electrodes)):
        scheme_tmp2 = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[i])
        scheme_tmp = su.merge_schemes(scheme_tmp, scheme_tmp2, folder + "tmp/")
    comp_scheme = su.merge_schemes(comp_scheme, scheme_tmp, folder + "tmp/")
scheme = comp_scheme

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
ert = pb.ERTManager()
syndata = ert.simulate(mesh, res=res, scheme=scheme,
                           verbose=config.general_bert_verbose, noiseLevel=config.sim_noise_level,
                           noiseAbs=config.sim_noise_abs)
syndata.markInvalid(syndata('rhoa') < 0)
syndata.removeInvalid()
syndata.save(folder + 'syndata.dat')

# invert
ert = pb.ERTManager()
inv = ert.invert(syndata, paraDX=config.inv_para_dx, maxCellArea=config.inv_max_cell_area,
                 lam=config.inv_lambda, verbose=config.general_bert_verbose)
ert.saveResult(folder)

