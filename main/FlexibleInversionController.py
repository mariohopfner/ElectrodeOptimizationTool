#!/usr/bin/env python

import logging
import datetime
import os

import numpy as np

import pybert as pb
import pygimli as pg
import pygimli.meshtools as mt

from main.ElectrodeUpdater import ElectrodeUpdater
import util.worldUtil as worldUtil
import main.InversionConfiguration as InversionConfiguration


class FlexibleInversionController:
    """ A class providing the main algorithm for an real-time experimental design based.

    This class is the main part of the algorithm to iteratively optimize the experimental design. Most configuration
    parameters are controlled within the InversionConfiguration object. The update criteria for which electrode
    configurations can be dynamically defined using a custom ElectrodeUpdater.

    Parameter:
        config: An InversionConfiguration object used to store all FlexibleInversionController-specific configuration
                parameters.
        electrode_updater: An object providing the logical basis for updating the electrode configurations.

    Typical usage example:
        fic = FlexibleInversionController(config, electrode_updater)
        fic.run()
    """
    def __init__(self, config: InversionConfiguration, electrode_updater: ElectrodeUpdater):
        self.__config = config
        self.__electrode_updater = electrode_updater

        self.__iteration = 0
        self.__folder = ''

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
        """ Creates the world model.

        Creates the world model based on the set world generator type.
        The simulated data is based on this world model.
        """
        # Create layered world
        if self.__config.world_gen == 'lay':
            self.__world = worldUtil.generate_dipped_layered_world(
                world_dim=[self.__config.world_x, self.__config.world_z],
                layer_borders=self.__config.world_layers, dipping_angle=self.__config.world_angle)
            return
        # Create homogeneous world with inclusion
        if self.__config.world_gen == 'incl':
            self.__world = worldUtil.generate_hom_world_with_inclusion(
                world_dim=[self.__config.world_x, self.__config.world_z],
                incl_start=self.__config.world_inclusion_start, incl_dim=self.__config.world_inclusion_dim)
            return
        # Create tiled world
        if self.__config.world_gen == 'tile':
            self.__world = worldUtil.generate_tiled_world(
                world_dim=[self.__config.world_x, self.__config.world_z],
                tile_size=[self.__config.world_tile_x, self.__config.world_tile_z])

    def __create_meshes(self):
        """ Creates all the used meshes.

        Creates the meshes for the simulation, the in-field inversion and the inversion after all data is collected.
        """
        # Add mesh nodes below the sensors based on
        for pos in self.__scheme.sensorPositions():
            self.__world.createNode(pos)
            self.__world.createNode(pos + pg.RVector3(0, -self.__config.finv_spacing / 2))
        # Create mesh for simulation based on the generated world
        self.__sim_mesh = mt.createMesh(poly=self.__world, quality=self.__config.sim_mesh_quality,
                                        area=self.__config.sim_mesh_maxarea)
        # Create parameter mesh for in-field inversion
        sensor_distance = self.__scheme.sensorPositions()[1][0] - self.__scheme.sensorPositions()[0][0]
        para_dx = self.__config.inv_dx / sensor_distance
        para_dz = self.__config.inv_dz / sensor_distance
        n_layers = int(self.__config.inv_depth/self.__config.inv_dz)
        self.__inv_mesh = mt.createParaMesh2DGrid(sensors=self.__scheme.sensorPositions(),
                                                  paraDX=para_dx, paraDZ=para_dz,
                                                  paraDepth=self.__config.inv_depth, nLayers=n_layers)
        # Create (probably finer) parameter mesh for a final inversion
        final_para_dx = self.__config.inv_final_dx / sensor_distance
        final_para_dz = self.__config.inv_final_dz / sensor_distance
        final_n_layers = int(self.__config.inv_final_depth / self.__config.inv_final_dz)
        self.__inv_final_mesh = mt.createParaMesh2DGrid(sensors=self.__scheme.sensorPositions(),
                                                  paraDX=final_para_dx, paraDZ=final_para_dz,
                                                  paraDepth=self.__config.inv_final_depth, nLayers=final_n_layers)

    def __create_res_array(self):
        """ Constructs the resistivity array based on given resistivities.

        Utility method to build the resistivity array to be interpreted by the pybert ERTManager.
        """
        i = 1
        # Add layer indicator and given resistivities to array
        for r in self.__config.world_resistivities:
            self.__res.append([i, r])
            i += 1

    def __initialize(self):
        """ Initializes the iterative inversion process provided by the FlexibleInversionController.

        Initializes the iterative inversion process, checks the given configuration parameters and creates some initial
        variables.

        Returns:
            Whether the initialization was successful.
        """
        # Create folder for saving all job-related information
        start_time = datetime.datetime.now()
        self.__folder = '../inversion_results/job-{:d}{:d}{:d}-{:d}.{:d}.{:d}{}/' \
            .format(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute,
                    start_time.second,
                    self.__config.general_folder_suffix)
        os.mkdir(self.__folder)
        # Initialize logging system
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s',
                            filename=self.__folder + 'job.log', level=logging.INFO)
        logging.info('Routine start time: ' + str(start_time))
        logging.info('Initializing logger successful. Logging to ' + self.__folder + 'job.log')
        logging.info('### STARTING INITIALIZATION PHASE')
        # Create temporary directory with main folder
        os.mkdir(self.__folder + 'tmp/')
        logging.info('Temporary directory created')
        # Broadcast folder to ElectrodeUpdater
        self.__electrode_updater.set_essentials(folder=self.__folder)
        # Check integrity of configuration file
        logging.info('Checking basic configuration file integrity...')
        config_integrity = self.__config.check_integrity()
        if config_integrity == 0:
            logging.info('Configuration file is integer!')
        else:
            logging.error('Configuration file is NOT integer! ABORTING!')
            logging.error('Error code ' + str(config_integrity) +
                          '. Check InversionConfiguration.check_integrity() for detailled information')
            return False
        # Print config values to log file for future reproducibility
        logging.info('Configuration parameters:')
        logging.info('#---------------#:')
        conf_values = self.__config.print_config()
        for i in range(len(conf_values)):
            logging.info(conf_values[i])
        logging.info('Electrode updater: ' + str(type(self.__electrode_updater)))
        logging.info('#---------------#:')
        # Init model and check model integrity
        logging.info('Creating world...')
        self.__create_world()
        logging.info('Creating configuration scheme...')
        self.__scheme = self.__electrode_updater.init_scheme()
        logging.info('Creating initial mesh...')
        self.__create_meshes()
        logging.info('Checking model integrity...')
        res_count = np.unique(ar=np.array(self.__sim_mesh.cellMarkers()), return_inverse=True)
        if len(res_count[0]) != len(self.__config.world_resistivities):
            logging.error('Marker count does NOT fit given resistivities! ABORTING!')
            logging.error('Allowed resistivities: {:d}, given resistivities: {:d}'.format(
                          len(res_count[0]), len(self.__config.world_resistivities)))
            return False
        logging.info('Creating resistivity array...')
        self.__create_res_array()
        logging.info('### INITIALIZATION COMPLETED')
        return True

    def __simulate(self, folder):
        """ Simulates a measurement set.

        Creates a set of synthetic data based on world, noise and given electrode configurations.

        Parameter:
            folder: The folder in which the resulting syndata.dat will be saved.
        """
        ert = pb.ERTManager()
        # Simulate synthetic data using pybert
        self.__syndata = ert.simulate(mesh=self.__sim_mesh, res=self.__res, scheme=self.__scheme,
                                      verbose=self.__config.general_bert_verbose,
                                      noiseLevel=self.__config.sim_noise_level,
                                      noiseAbs=self.__config.sim_noise_abs)
        # Removing invalid data
        self.__syndata.markInvalid(self.__syndata('rhoa') < 0)
        self.__syndata.removeInvalid()
        # Saving dataset to file
        self.__syndata.save(folder + 'syndata.dat')

    def __invert(self, folder):
        """ Inverts the synthetic dataset.

        Inverts the simulated, synthetic dataset created by __simulate(...). The default inversion mesh will be used.

        Parameter:
            folder: The folder in which the inversion result will be saved.
        """
        ert = pb.ERTManager()
        # Invert data
        self.__inv = ert.invert(data=self.__syndata,
                                lam=self.__config.inv_lambda, mesh=self.__inv_mesh,
                                verbose=self.__config.general_bert_verbose)
        # Save inversion results which are needed for further computations
        self.__fop = ert.fop
        self.__pd = ert.paraDomain
        # Save inversion results to file
        ert.saveResult(folder)

    def __final_invert(self, folder):
        """ Inverts the synthetic dataset on the final mesh.

        Inverts the simulated, synthetic dataset created by __simulate(...). The final inversion mesh will be used
        instead of the default one.

        Parameter:
            folder: The folder in which the inversion result will be saved.
        """
        ert = pb.ERTManager()
        # Invert data on final grid
        self.__final_inv = ert.invert(data=self.__syndata,
                                      lam=self.__config.inv_final_lambda, mesh=self.__inv_final_mesh,
                                      verbose=self.__config.general_bert_verbose)
        # Save inversion results to file
        ert.saveResult(folder)

    def __run_iteration(self):
        """ Performs a single iteration.

        Runs all steps needed for a single iteration including simulation, inversion and the electrode configuration
        update. Automatically does the final inversion when the last iteration is reached.
        """
        # Final inversion when the maximum iteration amount is reached.
        if self.__iteration >= self.__config.finv_max_iterations:
            logging.info('### MAX ITERATIONS REACHED')
            logging.info('Inverting data on final mesh ...')
            folder = self.__folder + 'final_inv/'
            os.mkdir(folder)
            self.__final_invert(folder)
            return False
        # Inverting data and computing new electrode configurations
        self.__iteration = self.__iteration + 1
        logging.info('### ITERATION ' + str(self.__iteration))
        iteration_subfolder = 'iteration' + str(self.__iteration) + '/'
        folder = self.__folder + iteration_subfolder
        os.mkdir(folder)
        if self.__iteration != 1:
            logging.info('Inverting data ...')
            self.__invert(folder)
            logging.info('Updating scheme ...')
            self.__scheme = self.__electrode_updater.update_scheme(
                old_scheme=self.__scheme, fop=self.__fop, inv_grid=self.__pd, inv_result=self.__inv,
                iteration_subdir=iteration_subfolder)
        # Simulate data with updated configurations
        logging.info('Simulating data ({:d} electrodes, {:d} configurations)...'.format(
            len(self.__scheme.sensorPositions()), len(self.__scheme('rhoa'))))
        self.__simulate(folder=folder)
        return True

    def run(self):
        """ Entry point for starting the iterative measurement process.

        Controls the basics of the iterative measurement process by initializing and running the single iterations.
        """
        if self.__initialize():
            run_loop = True
            while run_loop:
                run_loop = self.__run_iteration()
        logging.info('Routine end time: ' + str(datetime.datetime.now()))
