#!/usr/bin/env python

import os
import datetime

import pygimli as pg
import pybert as pb

import util.dataSimulator as ds
import util.worldGenerator as wg

########################################################################################################################
### PARAMETERS                                                                                                         #
########################################################################################################################
# general params,
param_bert_verbose = True

# world params
param_world_x = 400
param_world_y = 120
param_angle = 0
param_layers = [-10,-20]
param_resistivities = [100.0, 10.0, 100.0]

# simulation params
param_electrodes = [21]
#param_electrodes = [51]
param_mesh_quality = 34
param_noise_level = 0
param_noise_abs = 0
param_scheme = "slm"

# inversion params
param_paraDX = 0.3
param_maxCellArea = 10
param_lambda = 100

########################################################################################################################
### CODE                                                                                                               #
########################################################################################################################

# get starting time
start_time = datetime.datetime.now()

# set output folder based on starting time
folder = "../inversion_results/job-%d%d%d-%d.%d.%d/" \
         % (start_time.year,start_time.month,start_time.day,start_time.hour,start_time.minute,start_time.second)
os.mkdir(folder)

# save modelling and inversion parameters to file
paramFile = open(folder + "params.txt", "w")
paramFile.write("### WORLD ###\n")
paramFile.write("World: X %f, Y %f\n" % (param_world_x, param_world_y))
paramFile.write("Layers: %s with angle %f\n" % (param_layers, param_angle))
paramFile.write("Resistivities: %s\n" % param_resistivities)
paramFile.write("### SIMULATION ###\n")
paramFile.write("Electrodes: %s\n" % param_electrodes)
paramFile.write("Scheme: %s\n" % param_scheme)
paramFile.write("Mesh quality: %f\n" % param_mesh_quality)
paramFile.write("Noise: %f level and %f abs\n" % (param_noise_level, param_noise_abs))
paramFile.write("### SIMULATION ###\n")
paramFile.write("Grid params: %f paraDX and %f max cell area\n" % (param_paraDX, param_maxCellArea))
paramFile.write("Lambda: %f\n" % param_lambda)
paramFile.close()

# generate world by definitions
print("Generating world ...")
world = wg.generate_dipped_layered_world([param_world_x, param_world_y], param_layers, param_angle)
#world = wg. generate_hom_world_with_inclusion([param_world_x, param_world_y],[10, -10],[20, 20])
#world = wg.generate_layered_world([param_world_x, param_world_y],[50])
#scheme = pb.load(scheme_file)

# generate synthetic datasets
print("Simulating data ...")
syndata = []
for i_electrodes in range(len(param_electrodes)):
    print("with %d electrodes" % (param_electrodes[i_electrodes]))
    electrode_distribution = pg.utils.grange(start=0, end=param_world_x, n=param_electrodes[i_electrodes])
    scheme = pb.createData(elecs=electrode_distribution, schemeName=param_scheme)
    electrode_spacing = param_world_x/(param_electrodes[i_electrodes]-1)
    syndata.append(ds.simulate_data_from_world(world=world, scheme=scheme, resistivities=param_resistivities,
                                               electrode_spacing=electrode_spacing, mesh_quality=param_mesh_quality,
                                               noiseLevel=param_noise_level, noiseAbs=param_noise_abs,
                                               verbose=param_bert_verbose))
    syndata[i_electrodes].save(folder + "syndata-%d-%f.dat" % (param_electrodes[i_electrodes], electrode_spacing))

##scheme_file = "data1.dat"
##data = pb.DataContainerERT('data1.dat')

# invert datasets
print("Inverting data ...")
ert = pb.ERTManager()
models = []
for i_syndata in range(len(syndata)):
    print("with %d electrodes" % (param_electrodes[i_syndata]))
    #ert.fop.createJacobian(model=world,resp=syndata[i_syndata])
    models.append(
        ert.invert(syndata[i_syndata], paraDX=param_paraDX, maxCellArea=param_maxCellArea,
                                  lam=param_lambda, verbose=param_bert_verbose))
    ert.saveResult(folder + "inv-el%d/" % (param_electrodes[i_syndata]))

    cell_centers = ert.paraDomain.cellCenter()
    now = datetime.datetime.now()
    with open(folder + "inv-el%d/formatOutput.txt" % (param_electrodes[i_syndata]), 'w') as f:
        f.write("x z rho\n")
        for i in range(0, len(cell_centers)):
            f.write("%f %f %f\n" % (cell_centers[i][0],cell_centers[i][1],models[i_syndata][i]))
    print("Elapsed time: %f minutes" % ((datetime.datetime.now() - start_time).total_seconds() / 60))