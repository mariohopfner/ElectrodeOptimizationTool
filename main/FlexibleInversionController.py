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
        self.__electrodes = []
        self.__scheme = None
        self.__mesh = None
        self.__data = None
        self.__inv = None
        self.__fop = None
        self.__pd = None
        self.__res = []

    def __update_scheme(self, folder):
        self.__scheme = self.__electrode_updater.update_scheme(
            self.__scheme, self.__config.world_x,self.__config.finv_min_spacing,
            self.__config.finv_max_spacing, self.__fop, self.__pd, self.__inv)

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

        return -1

    def __create_scheme(self):
        self.__scheme = pb.createData(elecs=self.__electrodes, schemeName=self.__config.sim_schemes[0])
        for i in range(1,len(self.__config.sim_schemes)-1):
            scheme_tmp = pb.createData(elecs=self.__electrodes, schemeName=self.__config.sim_schemes[i])
            self.__scheme = su.merge_schemes(self.__scheme, scheme_tmp, self.__folder + "tmp/")
        return 0

    def __create_mesh(self):
        spacing = np.floor(len(self.__config.world_x/self.__electrodes))
        for pos in self.__scheme.sensorPositions():
            self.__world.createNode(pos)
            self.__world.createNode(pos + pg.RVector3(0, -spacing / 2))

        # create mesh from world
        self.__mesh = mt.createMesh(self.__world, quality=self.__config.sim_mesh_quality)
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
        self.__folder = "../inversion_results/job-%d%d%d-%d.%d.%d/" \
         % (start_time.year,start_time.month,start_time.day,start_time.hour,start_time.minute,start_time.second)
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
        logging.info("Creating first electrode setup...")
        self.__electrodes = self.__electrode_updater.init_electrodes(
            self.__config.world_x, self.__config.finv_max_spacing)
        logging.info("Creating configuration scheme...")
        self.__create_scheme()
        logging.info("Creating initial mesh...")
        self.__create_mesh()
        logging.info("Checking model integrity...")
        res_count = np.unique(np.array(self.__mesh.cellMarkers()), return_inverse=True)
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
        self.__data = ert.simulate(self.__mesh, res=self.__res, scheme=self.__scheme,
                                   verbose=self.__config.general_bert_verbose, noiseLevel=self.__config.sim_noise_level,
                                   noiseAbs=self.__config.sim_noise_abs)
        self.__data.markInvalid(self.__data('rhoa') < 0)
        self.__data.removeInvalid()
        self.__data.save(folder + 'syndata.dat')

    def __invert(self, folder):
        ert = pb.ERTManager()
        self.__inv = ert.invert(self.__data, paraDX=self.__config.inv_para_dx, maxCellArea=self.__config.inv_max_cell_area,
                   lam=self.__config.inv_lambda, verbose=self.__config.general_bert_verbose)
        self.__fop = ert.fop
        self.__pd = ert.paraDomain
        ert.saveResult(folder)

    def __run_iteration(self):
        # increment iteration
        if self.__iteration >= self.__config.finv_max_iterations:
            logging.info("### MAX ITERATIONS REACHED")
            return False
        self.__iteration = self.__iteration + 1
        logging.info("### ITERATION %d", self.__iteration)
        folder = self.__folder + "iteration" + str(self.__iteration) + "/"
        os.mkdir(folder)
        if self.__iteration != 1:
            logging.info("Updating scheme ...")
            self.__update_scheme(folder)
            logging.info("Updating mesh ...")
            self.__create_mesh()
        logging.info("Simulating data (%d electrodes, %d configurations)...",
                     len(self.__scheme.sensorPositions()), len(self.__scheme("rhoa")))
        self.__simulate(folder)
        logging.info("Inverting data ...")
        self.__invert(folder)
        return True

    def run(self):
        if self.__initialize():
            run_loop = True
            while run_loop:
                run_loop = self.__run_iteration()
        logging.info("Routine end time: %s", str(datetime.datetime.now()))
