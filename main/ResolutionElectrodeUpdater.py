#!/usr/bin/env python

import logging

from main.ElectrodeUpdater import ElectrodeUpdater
from main.SimpleRefiningElectrodeUpdater import SimpleRefiningElectrodeUpdater
import util.schemeUtil as su

import pygimli as pg
import pybert as pb
import numpy as np
import pygimli.utils.base as pgub

# ElectrodeUpdater that uses a resolution matrix to compute the optimal configuration
class ResolutionElectrodeUpdater(ElectrodeUpdater):

    def __init__(self, world_x, min_spacing, max_spacing):
        self.__world_x = world_x
        self.__min_spacing = min_spacing
        self.__max_spacing = max_spacing
        self.__comp_scheme = None
        self.__folder = None
        self.__j = None
        self.__r = None
        self.__iteration = 0

    def set_essentials(self, folder):
        self.__folder = folder

    # def __compute_resolution_matrix(self):
    #     logging.info("Computing pseudo inverse...")
    #     jp = np.linalg.pinv(self.__j)
    #     logging.info("Computing resolution matrix...")
    #     self.__r = np.matmul(jp,self.__j)

    def __create_comprehensive_scheme(self):
        logging.info('Creating comprehensive scheme...')
        schemes = ['wa', 'wb', 'pp', 'pd', 'dd', 'slm', 'hw', 'gr']
        electrode_counts = [np.ceil(self.__world_x / self.__min_spacing) + 1]
        comp_electrodes = [pg.utils.grange(start=0, end=self.__world_x, n=electrode_counts[0])]
        j = 0
        while np.floor((electrode_counts[j]-1)/2) == (electrode_counts[j]-1)/2:
            electrode_counts.append((electrode_counts[j]-1)/2+1)
            j = j + 1
            comp_electrodes.append(pg.utils.grange(start=0, end=self.__world_x, n=electrode_counts[j]))
        logging.info('Create scheme with configuration: ' + schemes[0])
        self.__comp_scheme = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[0])
        for j in range(1,len(comp_electrodes)):
            scheme_tmp = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[0])
            self.__comp_scheme = su.merge_schemes(self.__comp_scheme, scheme_tmp, self.__folder + "tmp/")

        for i in range(1,len(schemes)-1):
            scheme_tmp = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[i])
            for j in range(1, len(comp_electrodes)):
                scheme_tmp2 = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[i])
                scheme_tmp = su.merge_schemes(scheme_tmp, scheme_tmp2, self.__folder + "tmp/")
            logging.info('Merging with configuration: ' + schemes[i])
            self.__comp_scheme = su.merge_schemes(self.__comp_scheme, scheme_tmp, self.__folder + "tmp/")
        logging.info('Comprehensive scheme created')
        return 0

    def __compute_jacobian(self, mesh, res, scheme):
        ert = pb.ERTManager()
        logging.info("Simulating data...")
        data = ert.simulate(mesh=mesh, res=res, scheme=scheme, verbose=False, noiseLevel=0, noiseAbs=0)
        data.markInvalid(data('rhoa') < 0)
        data.removeInvalid()
        ert = pb.ERTManager()
        ert.setMesh(mesh,omitBackground=True)
        ert.setData(data)
        logging.info("Create Jacobian...")
        ert.fop.createJacobian(res)
        self.__j = pgub.gmat2numpy(ert.fop.jacobian())

    def __compute_next_configs(self, scheme_base, scheme_compr, j_base, j_compr, new_configs=200):
        electrode_count = len(scheme_compr.sensorPositions())

        nm = len(j_base[0]) # cell count
        nd = electrode_count * (electrode_count-1) * (electrode_count-2) * (electrode_count-3) / 8
        nd2 = len(j_compr)  # count of comprehensive configurations

        # compute j_add
        duplicate_indices = su.find_duplicate_configurations(scheme_compr, scheme_base)
        j_add = np.delete(j_compr,duplicate_indices,0)
        j_add_idx_dict = np.delete(range(nd2),duplicate_indices)

        # compute resolution matrices
        j_compr_inv = np.linalg.pinv(j_compr)
        r_compr = np.matmul(j_compr_inv, j_compr)
        j_base_inv = np.linalg.pinv(j_base)
        r_base = np.matmul(j_base_inv, j_base)

        # compute weightening vector
        gj_sum = np.zeros(nm)
        for i in range(nm):
            for j in range(nd2):
                gj_sum[i] += np.abs(j_compr[j,i])
            gj_sum[i] /= nd

        # compute goodness function
        gf = np.zeros(len(j_add))
        for i in range(len(j_add)):
            for j in range(nm):
                gf[i] += np.abs(j_add[i,j]) / gj_sum[j] * (1-r_base[j,j] / r_compr[j,j])

        sorted_indices = np.flip(np.argsort(gf))
        # for worst configs:
        # sorted_indices = np.argsort(gf)

        indices_to_use = j_add_idx_dict[sorted_indices[0:new_configs]]


        # TODO inner product LI needed?
        return indices_to_use

    def init_electrodes(self, world_x, max_spacing):
        electrode_count = np.ceil(world_x / max_spacing) + 1
        return pg.utils.grange(start=0, end=world_x, n=electrode_count)

    def update_scheme(self, old_scheme, world_x, min_spacing, max_spacing,
                          fop, inv_grid, inv_result):
        self.__iteration = self.__iteration + 1
        if self.__comp_scheme == None:
            self.__create_comprehensive_scheme()
        logging.info("Computing Jacobian for comprehensive scheme...")
        self.__compute_jacobian(inv_grid, inv_result, self.__comp_scheme)
        # compute resolution matrix from jacobian matrix
        logging.info("Computing goodness function...")
        # self.__compute_resolution_matrix()
        # cell_resolutions = np.diag(self.__r)
        # outpath = self.__folder + 'iteration' + str(self.__iteration) + '/' + 'resolutionMatrix.dat'
        # logging.info("Saving resistivity and resolution data to: " + outpath)
        # with open(outpath, 'w') as f:
        #     cell_centers = inv_grid.cellCenters()
        #     f.write('x z rho res\n')
        #     for i in range(len(inv_result)):
        #         f.write('%f %f %f %f\n' % (cell_centers[i][0],cell_centers[i][1],inv_result[i],cell_resolutions[i]))
        #     f.close()
        config_indices = self.__compute_next_configs(old_scheme, self.__comp_scheme,
                                                     pgub.gmat2numpy(fop.jacobian()), self.__j)
        logging.info("Goodness function computed")
        scheme_add = su.extract_configs_from_scheme(self.__comp_scheme, config_indices, self.__folder + 'tmp/')

        return su.merge_schemes(old_scheme, scheme_add, self.__folder + 'tmp/')
