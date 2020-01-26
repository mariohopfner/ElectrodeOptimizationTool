import logging

import numpy as np
from scipy.interpolate import griddata

import pybert as pb
import pygimli as pg

from main.ElectrodeUpdater import ElectrodeUpdater
import util.schemeUtil as su

# ElectrodeUpdater that uses a resolution matrix to compute the optimal configuration
class ResolutionElectrodeUpdater(ElectrodeUpdater):

    def __init__(self, world_x: float, spacing: float, base_configs: list, add_configs: list, gradient_weight: float,
                 addconfig_count: int):
        self.__world_x = world_x
        self.__spacing = spacing
        self.__base_configs = base_configs
        self.__add_configs = add_configs
        self.__gradient_weight = gradient_weight
        self.__addconfig_count = addconfig_count
        self.__comp_scheme = None
        self.__folder_tmp = None
        self.__iteration = 0

    def set_essentials(self, folder: str):
        self.__folder_tmp = folder + 'tmp/'

    def __create_comprehensive_scheme(self):
        logging.info('Creating comprehensive scheme...')
        schemes = self.__base_configs + self.__add_configs
        electrode_counts = [np.ceil(self.__world_x / self.__spacing) + 1]
        comp_electrodes = [pg.utils.grange(start=0, end=self.__world_x, n=electrode_counts[0])]
        for k in range(2,int(np.floor(electrode_counts[0]))):
            j = 0
            while np.floor((electrode_counts[j]-1)/k) == (electrode_counts[j]-1)/k:
                if (electrode_counts[j]-1)/k+1 > 4 and (electrode_counts[j]-1)/k+1 not in electrode_counts:
                    electrode_counts.append((electrode_counts[j]-1)/k+1)
                    j = len(electrode_counts) - 1
                    comp_electrodes.append(pg.utils.grange(start=0, end=self.__world_x, n=electrode_counts[j]))
                else:
                    electrode_counts.append((electrode_counts[j] - 1) / k + 1)
                    j = len(electrode_counts) - 1
        logging.info('Create scheme with configuration: ' + schemes[0])
        self.__comp_scheme = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[0])
        for j in range(1,len(comp_electrodes)):
            scheme_tmp = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[0])
            self.__comp_scheme = su.merge_schemes(self.__comp_scheme, scheme_tmp, self.__folder_tmp)

        for i in range(1,len(schemes)-1):
            scheme_tmp = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[i])
            for j in range(1, len(comp_electrodes)):
                scheme_tmp2 = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[i])
                scheme_tmp = su.merge_schemes(scheme_tmp, scheme_tmp2, self.__folder_tmp)
            logging.info('Merging with configuration: ' + schemes[i])
            self.__comp_scheme = su.merge_schemes(self.__comp_scheme, scheme_tmp, self.__folder_tmp)
        return 0

    def __compute_jacobian(self, mesh, res, scheme):
        ert = pb.ERTManager()
        logging.info("Simulating data...")
        data = ert.simulate(mesh=mesh, res=res, scheme=scheme, verbose=False, noiseLevel=0, noiseAbs=0)
        data.markInvalid(data('rhoa') < 0)
        data.removeInvalid()
        ert = pb.ERTManager()
        ert.setMesh(mesh, omitBackground=True)
        ert.setData(data)
        logging.info("Create Jacobian...")
        ert.fop.createJacobian(res)
        return pg.utils.base.gmat2numpy(ert.fop.jacobian())

    def __compute_next_configs(self, scheme_base, scheme_compr, j_base, j_compr,
                               mesh, cell_data):
        electrode_count = len(scheme_compr.sensorPositions())

        nm = len(j_base[0]) # cell count
        nd = int(electrode_count * (electrode_count-1) * (electrode_count-2) * (electrode_count-3) / 8)
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

        # compute weighting vector
        gj_sum = np.zeros(nm)
        for i in range(nm):
            for j in range(nd2):
                gj_sum[i] += np.abs(j_compr[j,i])
            gj_sum[i] /= nd

        # compute gradient weighing
        grad = np.zeros(nm)
        if self.__gradient_weight > 0:
            mesh.createNeighbourInfos()
            cc = mesh.cellCenters()
            for i in range(nm):
                n = 0
                cell_grad = 0
                if mesh.cells()[i].neighbourCell(0) is not None:
                    n += 1
                    i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(0)))
                    cell_grad += np.abs(cell_data[i] - cell_data[i_n]) / \
                                 ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                if mesh.cells()[i].neighbourCell(1) is not None:
                    n += 1
                    i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(1)))
                    cell_grad += np.abs(cell_data[i] - cell_data[i_n]) / \
                                 ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                if mesh.cells()[i].neighbourCell(2) is not None:
                    n += 1
                    i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(2)))
                    cell_grad += np.abs(cell_data[i] - cell_data[i_n]) / \
                                 ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                grad[i] = cell_grad / n
            grad /= max(grad)

            # TODO test: curvature
            curv = np.zeros(nm)
            for i in range(nm):
                n = 0
                cell_curv = 0
                if mesh.cells()[i].neighbourCell(0) is not None:
                    n += 1
                    i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(0)))
                    cell_curv += np.abs(grad[i] - grad[i_n]) / \
                                 ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                if mesh.cells()[i].neighbourCell(1) is not None:
                    n += 1
                    i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(1)))
                    cell_curv += np.abs(grad[i] - grad[i_n]) / \
                                 ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                if mesh.cells()[i].neighbourCell(2) is not None:
                    n += 1
                    i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(2)))
                    cell_curv += np.abs(grad[i] - grad[i_n]) / \
                                 ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                curv[i] = cell_curv / n
            curv /= max(curv)
            # TODO test: curvature

            outpath = self.__folder_tmp + '../gradient.dat'
            logging.info("Saving resistivity and resolution data to: " + outpath)
            with open(outpath, 'w') as f:
                cell_centers = mesh.cellCenters()
                f.write('x z rho grad curv\n')
                for i in range(len(cell_data)):
                    f.write('%f %f %f %f %f\n' % (cell_centers[i][0],cell_centers[i][1],cell_data[i],grad[i], curv[i]))
                f.close()

        # compute goodness function
        # TODO adapt grad scaling?
        gf = np.zeros(len(j_add))
        for i in range(len(j_add)):
            for j in range(nm):
                gf[i] += np.abs(j_add[i, j]) / gj_sum[j] * (1 + self.__gradient_weight * grad[j]) * \
                         (1 - r_base[j, j] / r_compr[j, j])

        sorted_indices = np.flip(np.argsort(gf))

        if len(sorted_indices) > self.__addconfig_count:
            indices_to_use = j_add_idx_dict[sorted_indices[0:self.__addconfig_count]]
        else:
            indices_to_use = j_add_idx_dict[sorted_indices]

        # TODO inner product LI should be used!
        return indices_to_use

    def init_scheme(self):
        electrode_count = np.ceil(self.__world_x / self.__spacing) + 1
        if np.floor((electrode_count - 1) / 2) == (electrode_count - 1) / 2:
            electrode_count = (electrode_count - 1) / 2 + 1
        else:
            logging.info("Electrodes could not be divided in half for initial configuration! Using all electrodes!")

        electrodes = pg.utils.grange(start=0, end=self.__world_x, n=electrode_count)
        scheme = pb.createData(elecs=electrodes, schemeName=self.__base_configs[0])
        for i in range(1, len(self.__base_configs) - 1):
            scheme_tmp = pb.createData(elecs=electrodes, schemeName=self.__base_configs[i])
            scheme = su.merge_schemes(scheme, scheme_tmp, self.__folder_tmp)
        return scheme

    def update_scheme(self, old_scheme, fop, inv_grid, inv_result):
        self.__iteration = self.__iteration + 1
        if self.__comp_scheme == None:
            self.__create_comprehensive_scheme()
        logging.info("Computing Jacobian for comprehensive scheme...")
        j_compr = self.__compute_jacobian(inv_grid, inv_result, self.__comp_scheme)
        # compute resolution matrix from jacobian matrix
        logging.info("Computing goodness function...")
        config_indices = self.__compute_next_configs(old_scheme, self.__comp_scheme,
                                                     pg.utils.base.gmat2numpy(fop.jacobian()),j_compr,
                                                     inv_grid, inv_result)

        scheme_add = su.extract_configs_from_scheme(self.__comp_scheme, config_indices, self.__folder_tmp)

        return su.merge_schemes(old_scheme, scheme_add, self.__folder_tmp)
