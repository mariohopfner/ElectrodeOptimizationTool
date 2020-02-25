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
config = InversionConfiguration(general_bert_verbose=True, general_folder_suffix='-testtile',
                                world_x=200, world_y=100, world_resistivities=[10,100], world_gen='tile',
                                world_layers=[], world_angle=0,
                                world_inclusion_start=[50,-20], world_inclusion_dim=[20,10],
                                world_tile_x=40, world_tile_y=5,
                                world_electrode_offset=0,
                                sim_mesh_quality=34, sim_mesh_maxarea=30, sim_noise_level=5, sim_noise_abs=1e-6,
                                inv_lambda=50, inv_dx=2, inv_dz=2, inv_depth=50,
                                inv_final_lambda=0, inv_final_dx=0, inv_final_dz=0, inv_final_depth=0,
                                finv_max_iterations=5, finv_spacing=2, finv_base_configs=['dd'],
                                finv_add_configs=['wa', 'wb', 'pp', 'pd', 'slm', 'hw', 'gr'],
                                finv_gradient_weight=0, finv_addconfig_count=100, finv_li_threshold=1)

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

if config.world_gen == "tile":
    world = wg.generate_tiled_world(world_dim=[config.world_x, config.world_y],
                                           tile_size=[config.world_tile_x, config.world_tile_y])

# create electrodes
electrode_count = np.ceil((config.world_x - 2 * config.world_electrode_offset) / config.finv_spacing) + 1
electrodes = pg.utils.grange(start=config.world_electrode_offset, end=config.world_x-config.world_electrode_offset,
                             n=electrode_count)

# create scheme
#schemes = ['wa', 'wb', 'pp', 'pd', 'dd', 'slm', 'hw', 'gr']
#schemes = ['dd','slm','pp']
schemes = ['wa','wb','dd','slm','hw','gr']
electrode_counts = [np.ceil((config.world_x - 2 * config.world_electrode_offset) / config.finv_spacing) + 1]
comp_electrodes = [pg.utils.grange(start=config.world_electrode_offset, end=config.world_x-config.world_electrode_offset, n=electrode_counts[0])]
j = 0
while np.floor((electrode_counts[j]-1)/2) == (electrode_counts[j]-1)/2:
    electrode_counts.append((electrode_counts[j]-1)/2+1)
    j = j + 1
    comp_electrodes.append(pg.utils.grange(start=config.world_electrode_offset, end=config.world_x-config.world_electrode_offset, n=electrode_counts[j]))
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
spacing = scheme.sensorPositions()[1][0] - scheme.sensorPositions()[0][0]
for pos in scheme.sensorPositions():
    world.createNode(pos)
    world.createNode(pos + pg.RVector3(0, -spacing / 2))

# create mesh from world
mesh = mt.createMesh(world, quality=config.sim_mesh_quality)

# create inversion mesh
sensor_distance = scheme.sensorPositions()[1][0] - scheme.sensorPositions()[0][0]
para_dx = config.inv_dx / sensor_distance
para_dz = config.inv_dz / sensor_distance
n_layers = int(config.inv_depth/config.inv_dz)
inv_mesh = mt.createParaMesh2DGrid(sensors=scheme.sensorPositions(), paraDX=para_dx, paraDZ=para_dz,
                                          paraDepth=config.inv_depth, nLayers=n_layers)

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
syndata.markInvalid(syndata('rhoa') <= 0)
syndata.removeInvalid()
syndata.save(folder + 'syndata.dat')

# invert
ert = pb.ERTManager()
inv = ert.invert(syndata, mesh=inv_mesh,
                 lam=config.inv_lambda, verbose=config.general_bert_verbose)
ert.saveResult(folder)

