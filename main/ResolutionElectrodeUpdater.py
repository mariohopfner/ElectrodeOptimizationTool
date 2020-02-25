import logging

import numpy as np
from scipy.interpolate import griddata

import pybert as pb
import pygimli as pg

from main.ElectrodeUpdater import ElectrodeUpdater
import util.schemeUtil as su

# ElectrodeUpdater that uses a resolution matrix to compute the optimal configuration
class ResolutionElectrodeUpdater(ElectrodeUpdater):

    def __init__(self, world_x: float, spacing: float, electrode_offset: float, base_configs: list, add_configs: list, gradient_weight: float,
                 addconfig_count: int, li_threshold: float):
        self.__world_x = world_x
        self.__spacing = spacing
        self.__electrode_offset = electrode_offset
        self.__base_configs = base_configs
        self.__add_configs = add_configs
        self.__gradient_weight = gradient_weight
        self.__addconfig_count = addconfig_count
        self.__li_threshold = li_threshold
        self.__comp_scheme = None
        self.__folder_tmp = None
        self.__iteration = 0

    def set_essentials(self, folder: str):
        self.__folder_tmp = folder + 'tmp/'

    def __create_comprehensive_scheme(self):
        logging.info('Creating comprehensive scheme...')
        schemes = self.__base_configs + self.__add_configs
        electrode_counts = [np.ceil((self.__world_x - 2 * self.__electrode_offset)/ self.__spacing) + 1]
        comp_electrodes = [pg.utils.grange(start=self.__electrode_offset, end=self.__world_x - self.__electrode_offset,
                                           n=electrode_counts[0])]
        for k in range(2,int(np.floor(electrode_counts[0]))):
            j = 0
            while np.floor((electrode_counts[j]-1)/k) == (electrode_counts[j]-1)/k:
                if (electrode_counts[j]-1)/k+1 > 4 and (electrode_counts[j]-1)/k+1 not in electrode_counts:
                    electrode_counts.append((electrode_counts[j]-1)/k+1)
                    j = len(electrode_counts) - 1
                    comp_electrodes.append(pg.utils.grange(start=self.__electrode_offset,
                                                           end=self.__world_x - self.__electrode_offset,
                                                           n=electrode_counts[j]))
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

    def __compute_inner_products(self, j_base, j_add, k, nm):
        n_base = len(j_base)
        li = np.zeros(n_base)
        for i in range(n_base):
            for j in range(nm):
                li[i] += j_base[i][j] * j_add[k][j]
            li[i] /= (np.linalg.norm(j_base[i]) * np.linalg.norm(j_add[k]))
            li[i] = np.abs(li[i])
        return li

    def __compute_next_configs(self, scheme_base, scheme_compr, j_base, j_compr,
                               mesh, cell_data, iteration_subdir):
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

            outpath = self.__folder_tmp + '../' + iteration_subdir + 'gradient.dat'
            logging.info("Saving resistivity and resolution data to: " + outpath)
            with open(outpath, 'w') as f:
                cell_centers = mesh.cellCenters()
                f.write('x z rho grad\n')
                for i in range(len(cell_data)):
                    f.write('%f %f %f %f\n' % (cell_centers[i][0],cell_centers[i][1],cell_data[i],grad[i]))
                f.close()

        # compute goodness function
        # TODO adapt grad scaling?
        res_gf = np.zeros(len(j_add))
        grad_gf = np.zeros(len(j_add))
        for i in range(len(j_add)):
            for j in range(nm):
                res_gf[i] += np.abs(j_add[i, j]) / gj_sum[j] * (1 - r_base[j, j] / r_compr[j, j])
                grad_gf[i] += grad[j]

        sorted_indices_res = np.flip(np.argsort(res_gf))
        sorted_indices_grad = np.flip(np.argsort(grad_gf))

        grad_count = int(np.floor(self.__addconfig_count*self.__gradient_weight))
        res_count = self.__addconfig_count - grad_count

        indices_to_use = []

        added_indices = 0
        idx_rank = 0
        while added_indices < res_count:
            if idx_rank >= len(sorted_indices_res):
                break

            idx_to_add = sorted_indices_res[idx_rank]
            li = self.__compute_inner_products(j_base, j_add, idx_to_add, nm)
            li_accepted = True
            for i in range(len(li)):
                if li[i] >= self.__li_threshold:
                    li_accepted = False
            if li_accepted:
                indices_to_use.append(j_add_idx_dict[idx_to_add])
                added_indices += 1
            idx_rank += 1

        logging.info("LI: Skipping %d configurations", idx_rank - res_count)
        if grad_count > 0:
            grad_count += res_count - added_indices
            if len(sorted_indices_grad) > grad_count:
                indices_to_use = indices_to_use + list(j_add_idx_dict[sorted_indices_grad[0:grad_count]])
            else:
                indices_to_use = indices_to_use + list(j_add_idx_dict[sorted_indices_grad])

        return np.unique(indices_to_use)

    def init_scheme(self):
        electrode_count = np.ceil((self.__world_x - 2 * self.__electrode_offset) / self.__spacing) + 1
        if np.floor((electrode_count - 1) / 2) == (electrode_count - 1) / 2:
            electrode_count = (electrode_count - 1) / 2 + 1
        else:
            logging.info("Electrodes could not be divided in half for initial configuration! Using all electrodes!")

        electrodes = pg.utils.grange(start=self.__electrode_offset, end=self.__world_x-self.__electrode_offset,
                                     n=electrode_count)
        scheme = pb.createData(elecs=electrodes, schemeName=self.__base_configs[0])
        for i in range(1, len(self.__base_configs) - 1):
            scheme_tmp = pb.createData(elecs=electrodes, schemeName=self.__base_configs[i])
            scheme = su.merge_schemes(scheme, scheme_tmp, self.__folder_tmp)
        return scheme

    def update_scheme(self, old_scheme, fop, inv_grid, inv_result, iteration_subdir):
        self.__iteration = self.__iteration + 1
        if self.__comp_scheme == None:
            self.__create_comprehensive_scheme()
        logging.info("Computing Jacobian for comprehensive scheme...")
        j_compr = self.__compute_jacobian(inv_grid, inv_result, self.__comp_scheme)
        # compute resolution matrix from jacobian matrix
        logging.info("Computing goodness function...")
        config_indices = self.__compute_next_configs(old_scheme, self.__comp_scheme,
                                                     pg.utils.base.gmat2numpy(fop.jacobian()),j_compr,
                                                     inv_grid, inv_result, iteration_subdir)

        outpath = self.__folder_tmp + '../' + iteration_subdir + 'configs_to_add.txt'
        logging.info("Saving computed configs to: " + outpath)
        with open(outpath, 'w') as f:
            for i in range(len(config_indices)):
                f.write('%d\n' % (config_indices[i]))
            f.close()

        scheme_add = su.extract_configs_from_scheme(self.__comp_scheme, config_indices, self.__folder_tmp)

        return su.merge_schemes(old_scheme, scheme_add, self.__folder_tmp)
