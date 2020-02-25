#!/usr/bin/env python

import logging
import datetime
import os

import numpy as np

import pybert as pb
import pygimli as pg
import pygimli.meshtools as mt

import util.worldGenerator as wg
import util.InversionConfiguration as InversionConfiguration
import util.schemeUtil as su
from main.ElectrodeUpdater import ElectrodeUpdater

class FlexibleInversionController:
    def __init__(self, config: InversionConfiguration, electrode_updater: ElectrodeUpdater):
        self.__config = config
        self.__electrode_updater = electrode_updater
        self.__iteration = 0
        self.__is_initialized = False
        self.__folder = ""

        self.__world = None
        self.__scheme = None
        self.__sim_mesh = None
        self.__inv_mesh = None
        self.__inv_final_mesh = None
        self.__syndata = None
        self.__inv = None
        self.__final_inv = None
        self.__fop = None
        self.__pd = None
        self.__res = []

    def __create_world(self):
        if self.__config.world_gen == "lay":
            self.__world = wg.generate_dipped_layered_world(
                [self.__config.world_x, self.__config.world_y], self.__config.world_layers, self.__config.world_angle)
            return 0

        if self.__config.world_gen == "incl":
            self.__world = wg.generate_hom_world_with_inclusion(
                [self.__config.world_x, self.__config.world_y],
                self.__config.world_inclusion_start, self.__config.world_inclusion_dim)
            return 0

        if self.__config.world_gen == "tile":
            self.__world = wg.generate_tiled_world(world_dim=[self.__config.world_x, self.__config.world_y],
                                                   tile_size=[self.__config.world_tile_x, self.__config.world_tile_y])
            return 0

        return -1

    def __create_meshs(self):
        for pos in self.__scheme.sensorPositions():
            self.__world.createNode(pos)
            self.__world.createNode(pos + pg.RVector3(0, -self.__config.finv_spacing / 2))

        # create mesh from world
        self.__sim_mesh = mt.createMesh(self.__world, quality=self.__config.sim_mesh_quality,
                                        area=self.__config.sim_mesh_maxarea)

        # create mesh for inversion
        sensor_distance = self.__scheme.sensorPositions()[1][0] - self.__scheme.sensorPositions()[0][0]
        para_dx = self.__config.inv_dx / sensor_distance
        para_dz = self.__config.inv_dz / sensor_distance
        n_layers = int(self.__config.inv_depth/self.__config.inv_dz)
        self.__inv_mesh = mt.createParaMesh2DGrid(sensors=self.__scheme.sensorPositions(),
                                                  paraDX=para_dx, paraDZ=para_dz,
                                                  paraDepth=self.__config.inv_depth, nLayers=n_layers)

        # create mesh for inversion
        final_para_dx = self.__config.inv_final_dx / sensor_distance
        final_para_dz = self.__config.inv_final_dz / sensor_distance
        final_n_layers = int(self.__config.inv_final_depth / self.__config.inv_final_dz)
        self.__inv_final_mesh = mt.createParaMesh2DGrid(sensors=self.__scheme.sensorPositions(),
                                                  paraDX=final_para_dx, paraDZ=final_para_dz,
                                                  paraDepth=self.__config.inv_final_depth, nLayers=final_n_layers)

        return 0

    def __create_res_array(self):
        self.__res = []
        i = 1
        for r in self.__config.world_resistivities:
            self.__res.append([i, r])
            i = i + 1

    def __initialize(self):
        # cancel if controller is already initialized
        if self.__is_initialized:
            return True
        # set up job folder
        start_time = datetime.datetime.now()
        self.__folder = "../inversion_results/job-%d%d%d-%d.%d.%d%s/" \
         % (start_time.year,start_time.month,start_time.day,start_time.hour,start_time.minute,start_time.second,
            self.__config.general_folder_suffix)
        os.mkdir(self.__folder)
        # init logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(format="%(asctime)s:%(levelname)s: %(message)s",
                            filename=self.__folder + "job.log", level=logging.INFO)
        logging.info("Routine start time: %s", str(start_time))
        logging.info("Initializing logger successful. Logging to %s", self.__folder + "job.log")
        logging.info("### STARTING INITIALIZATION PHASE")
        # create temporary directory
        os.mkdir(self.__folder + "tmp/")
        logging.info("Temporary directory created")
        # set logger and folder within electrode updater
        self.__electrode_updater.set_essentials(self.__folder)

        # check basic config file integrity
        logging.info("Checking basic configuration file integrity...")
        config_integrity = self.__config.check_integrity()
        if config_integrity == 0:
            logging.info("Configuration file is integer!")
        else:
            logging.error("Configuration file is NOT integer! ABORTING!")
            logging.error("Error code %d. Check InversionConfiguration.check_integrity() for detailled information",
                          config_integrity)
            return False
        # log config values
        logging.info("Configuration parameters:")
        logging.info("#---------------#:")
        conf_values = self.__config.print_config()
        for i in range(len(conf_values)):
            logging.info(conf_values[i])
        logging.info("Electrode updater: : %s", str(type(self.__electrode_updater)))
        logging.info("#---------------#:")
        # check model integrity
        logging.info("Creating world...")
        self.__create_world()
        logging.info("Creating configuration scheme...")
        self.__scheme = self.__electrode_updater.init_scheme()
        logging.info("Creating initial mesh...")
        self.__create_meshs()
        logging.info("Checking model integrity...")
        res_count = np.unique(np.array(self.__sim_mesh.cellMarkers()), return_inverse=True)
        if len(res_count[0]) != len(self.__config.world_resistivities):
            logging.error("Marker count does NOT fit given resistivities! ABORTING!")
            logging.error("Allowed resistivities: %d, given resistivities: %d",
                          len(res_count[0]), len(self.__config.world_resistivities))
            return False
        logging.info("Creating resistivity array...")
        self.__create_res_array()
        logging.info("### INITIALIZATION COMPLETED")
        self.__is_initialized = True
        return True

    def __simulate(self, folder):
        ert = pb.ERTManager()
        self.__syndata = ert.simulate(self.__sim_mesh, res=self.__res, scheme=self.__scheme,
                                      verbose=self.__config.general_bert_verbose,
                                      noiseLevel=self.__config.sim_noise_level,
                                      noiseAbs=self.__config.sim_noise_abs)
        self.__syndata.markInvalid(self.__syndata('rhoa') < 0)
        self.__syndata.removeInvalid()
        self.__syndata.save(folder + 'syndata.dat')

    def __invert(self, folder):
        ert = pb.ERTManager()
        self.__inv = ert.invert(self.__syndata,
                                lam=self.__config.inv_lambda, mesh=self.__inv_mesh,
                                verbose=self.__config.general_bert_verbose)
        self.__fop = ert.fop
        self.__pd = ert.paraDomain
        ert.saveResult(folder)

    def __final_invert(self, folder):
        ert = pb.ERTManager()
        self.__final_inv = ert.invert(self.__syndata,
                                lam=self.__config.inv_final_lambda, mesh=self.__inv_final_mesh,
                                verbose=self.__config.general_bert_verbose)
        ert.saveResult(folder)

    def __run_iteration(self):
        if self.__iteration >= self.__config.finv_max_iterations:
            logging.info("### MAX ITERATIONS REACHED")
            logging.info("Inverting data on final mesh ...")
            folder = self.__folder + 'final_inv/'
            os.mkdir(folder)
            self.__final_invert(folder)
            return False

        self.__iteration = self.__iteration + 1
        logging.info("### ITERATION %d", self.__iteration)
        iteration_subfolder = 'iteration' + str(self.__iteration) + '/'
        folder = self.__folder + iteration_subfolder
        os.mkdir(folder)
        if self.__iteration != 1:
            logging.info("Inverting data ...")
            self.__invert(folder)
            logging.info("Updating scheme ...")
            self.__scheme = self.__electrode_updater.update_scheme(self.__scheme, self.__fop, self.__pd, self.__inv,
                                                                   iteration_subfolder)
        logging.info("Simulating data (%d electrodes, %d configurations)...",
                     len(self.__scheme.sensorPositions()), len(self.__scheme("rhoa")))
        self.__simulate(folder)
        return True


    # def __run_iteration_old(self):
    #     # TODO resort and add final inversion
    #     # increment iteration
    #     if self.__iteration >= self.__config.finv_max_iterations:
    #         logging.info("### MAX ITERATIONS REACHED")
    #         return False
    #     self.__iteration = self.__iteration + 1
    #     logging.info("### ITERATION %d", self.__iteration)
    #     iteration_subfolder = 'iteration' + str(self.__iteration) + '/'
    #     folder = self.__folder + iteration_subfolder
    #     os.mkdir(folder)
    #     if self.__iteration != 1:
    #         logging.info("Updating scheme ...")
    #         self.__scheme = self.__electrode_updater.update_scheme(self.__scheme, self.__fop, self.__pd, self.__inv,
    #                                                                iteration_subfolder)
    #     logging.info("Simulating data (%d electrodes, %d configurations)...",
    #                  len(self.__scheme.sensorPositions()), len(self.__scheme("rhoa")))
    #     self.__simulate(folder)
    #     logging.info("Inverting data ...")
    #     self.__invert(folder)
    #     return True

    def run(self):
        if self.__initialize():
            run_loop = True
            while run_loop:
                run_loop = self.__run_iteration()
        logging.info("Routine end time: %s", str(datetime.datetime.now()))
