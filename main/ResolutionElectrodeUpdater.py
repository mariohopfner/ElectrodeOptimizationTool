import logging

import numpy as np
import pybert as pb
import pygimli as pg

from main.ElectrodeUpdater import ElectrodeUpdater
import util.schemeUtil as schemeUtil

class ResolutionElectrodeUpdater(ElectrodeUpdater):
    """ An ElectrodeUpdater-implementation providing the update based on subsurface resolution.

    This class is an implementation of the abstract ElectrodeUpdater-class providing electrode updates based on the
    optimal subsurface resolution and the subsurface resistivity change gradient (as configured). The
    ResolutionElectrodeUpdater uses a thinned out electrode set for initial data collection.

    Parameter:
        world_x: A float describing the worlds x dimension.
        spacing: A float describing the distance between electrodes.
        electrode_offset: A float describing the offset of the outer electrodes to the defined world border.
        base_configs: A list with strings indicating the configuration types used for initial data acquisition.
        add_configs:  A list with strings indicating the configuration types used for data acquisition.
        gradient_weight: A float indicating the weight of the subsurface resistivity gradient compared to the subsurface
                         resolution. 0 disables the usage of the gradients, 1 only uses the gradient as criterion.
        addconfig_count: Number of configurations to be added per iteration.
        li_threshold: A float, which li value is the highest possible for accepting an electrode configuration.

    Typical usage example:
        electrode_updater = ResolutionElectrodeUpdater(...)
        fic = FlexibleInversionController(..., electrode_updater)
    """
    def __init__(self, world_x: float, spacing: float, electrode_offset: float, base_configs: list, add_configs: list,
                 gradient_weight: float, addconfig_count: int, li_threshold: float):
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
        """ Sets a few parameters at runtime.

        Utility method for setting parameters at runtime (or after FlexibleInversionController construction) which can
        be set before.

        Parameter:
            folder: the folder which is used for persisting iteration-specific data
        """
        self.__folder_tmp = folder + 'tmp/'

    def __create_comprehensive_scheme(self):
        """ Creates a scheme containing most conventional electrode configurations.

        Utility method to create a scheme file with most of conventional electrode configurations, including Wenner,
        Schlumberger, Pole-Pole, Dipole-Dipole and a few more. This creates a pool of configurations which can be used
        by the algorithm to distinguish the optimal configuration set.
        """
        logging.info('Creating comprehensive scheme...')
        # Merge all configured scheme types
        schemes = self.__base_configs + self.__add_configs
        # Compute needed electrode information
        electrode_counts = [np.ceil((self.__world_x - 2 * self.__electrode_offset)/ self.__spacing) + 1]
        comp_electrodes = [pg.utils.grange(start=self.__electrode_offset, end=self.__world_x - self.__electrode_offset,
                                           n=electrode_counts[0])]
        # Compute electrode counts for virtually thinned-out configurations
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
        # Create initial scheme for all selected electrode counts
        logging.info('Create scheme with configuration: ' + schemes[0])
        self.__comp_scheme = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[0])
        for j in range(1,len(comp_electrodes)):
            scheme_tmp = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[0])
            self.__comp_scheme = schemeUtil.merge_schemes(scheme1=self.__comp_scheme, scheme2=scheme_tmp,
                                                          tmp_dir=self.__folder_tmp)
        # Merge all selected schemes for all selected electrode counts
        for i in range(1,len(schemes)-1):
            scheme_tmp = pb.createData(elecs=comp_electrodes[0], schemeName=schemes[i])
            for j in range(1, len(comp_electrodes)):
                scheme_tmp2 = pb.createData(elecs=comp_electrodes[j], schemeName=schemes[i])
                scheme_tmp = schemeUtil.merge_schemes(scheme1=scheme_tmp, scheme2=scheme_tmp2, tmp_dir=self.__folder_tmp)
            logging.info('Merging with configuration: ' + schemes[i])
            self.__comp_scheme = schemeUtil.merge_schemes(scheme1=self.__comp_scheme, scheme2=scheme_tmp,
                                                          tmp_dir=self.__folder_tmp)

    def __compute_jacobian(self, mesh: pg.Mesh, res: np.ndarray, scheme: pb.DataContainerERT):
        """ Computes the Jacobian (sensitivity) matrix.

        Computes the Jacobian (sensitivity) matrix based on a given mesh with resistivities and a set of electrode configurations.

        Parameter:
            mesh: The mesh used as approximate subsurface model.
            res: The resistivity vector containing the resistivities for the mesh cells
            scheme: The electrode configuration scheme for sensitivity calculation

        Returns:
            The Jacobian matrix as numpy matrix
        """
        ert = pb.ERTManager()
        # Simulate data for brute-force sensitivity calculation
        logging.info('Simulating data...')
        data = ert.simulate(mesh=mesh, res=res, scheme=scheme, verbose=False, noiseLevel=0, noiseAbs=0)
        data.markInvalid(data('rhoa') < 0)
        data.removeInvalid()
        # Set essential data for Jacobian computation
        ert = pb.ERTManager()
        ert.setMesh(mesh, omitBackground=True)
        ert.setData(data)
        # Compute Jacobian matrix
        logging.info('Create Jacobian...')
        ert.fop.createJacobian(res)
        return pg.utils.base.gmat2numpy(ert.fop.jacobian())

    def __compute_inner_products(self, j_base: np.ndarray, j_add: np.ndarray, k: int, nm: int):
        """ Computes the inner products of possible configurations to add.

        Method to compute the inner products of configuration sensitivities of possibly added configurations and
        already used configurations.

        Parameter:
            j_base: Sensitivities of configurations already in use.
            j_add: Sensitivities of configurations not in use.
            k: Index of configuration to be checked.
            nm: Mesh cell count.

        Returns:
            Vector containing the computed linear dependencies (0 -> fully independent, 1 -> fully dependent)
        """
        n_base = len(j_base)
        li = np.zeros(n_base)
        # Compute inner products using every base configuration and every cell
        for i in range(n_base):
            for j in range(nm):
                li[i] += j_base[i][j] * j_add[k][j]
            li[i] /= (np.linalg.norm(j_base[i]) * np.linalg.norm(j_add[k]))
            li[i] = np.abs(li[i])
        return li

    def __compute_next_configs(self, scheme_base: pb.DataContainerERT, scheme_compr: pb.DataContainerERT,
                               j_base: np.ndarray, j_compr: np.ndarray, mesh: pg.Mesh, cell_data: pg.RVector,
                               iteration_subdir: str):
        """ Computes the additional electrode configurations.

        Method that computes the electrode configurations which are the next most optimal based on subsurface resolution
        and other criteria.

        Parameter:
            scheme_base: Scheme containing already used electrode configurations.
            scheme_compr: Scheme containing all possible electrode configurations.
            j_base: Jacobian matrix for scheme_base.
            j_compr: Jacobian matrix for scheme_compr.
            mesh: Subsurface mesh for which the resistivities were computed.
            cell_data: Mesh cell resistivities for gradient computations.
            iteration_subdir: Subfolder to save files for debugging and testing purposes.

        Returns:
            The indices of the electrode configurations to be added to the measurement scheme.
        """
        electrode_count = len(scheme_compr.sensorPositions())
        nm = len(j_base[0]) # cell count
        nd = int(electrode_count * (electrode_count-1) * (electrode_count-2) * (electrode_count-3) / 8)
        nd2 = len(j_compr)  # count of comprehensive configurations
        # Compute j_add by subtracting j_base from j_compr
        duplicate_indices = schemeUtil.find_duplicate_configurations(scheme1=scheme_compr, scheme2=scheme_base)
        j_add = np.delete(arr=j_compr,obj=duplicate_indices,axis=0)
        j_add_idx_dict = np.delete(arr=range(nd2),obj=duplicate_indices)
        # Compute resolution matrices
        j_compr_inv = np.linalg.pinv(j_compr)
        r_compr = np.matmul(j_compr_inv, j_compr)
        j_base_inv = np.linalg.pinv(j_base)
        r_base = np.matmul(j_base_inv, j_base)
        # Compute weighting vector
        gj_sum = np.zeros(nm)
        for i in range(nm):
            for j in range(nd2):
                gj_sum[i] += np.abs(j_compr[j,i])
            gj_sum[i] /= nd
        # Compute gradient weighting
        grad = np.zeros(nm)
        if self.__gradient_weight > 0:
            mesh.createNeighbourInfos()
            cc = mesh.cellCenters()
            for i in range(nm):
                n = 0
                cell_grad = 0
                for j in range(mesh.cells()[i].neighbourCellCount()):
                    if mesh.cells()[i].neighbourCell(j) is not None:
                        n += 1
                        i_n = mesh.cells().index((mesh.cells()[i].neighbourCell(j)))
                        cell_grad += np.abs(cell_data[i] - cell_data[i_n]) / \
                                     ((cc[i][0] - cc[i_n][0]) ** 2 + (cc[i][1] - cc[i_n][1]) ** 2) ** 0.5
                grad[i] = cell_grad / n
            grad /= max(grad)
            outpath = self.__folder_tmp + '../' + iteration_subdir + 'gradient.dat'
            logging.info('Saving resistivity and resolution data to: ' + outpath)
            with open(outpath, 'w') as f:
                cell_centers = mesh.cellCenters()
                f.write('x z rho grad\n')
                for i in range(len(cell_data)):
                    f.write('%f %f %f %f\n' % (cell_centers[i][0],cell_centers[i][1],cell_data[i],grad[i]))
                f.close()
        # Compute goodness function
        res_gf = np.zeros(len(j_add))
        grad_gf = np.zeros(len(j_add))
        for i in range(len(j_add)):
            for j in range(nm):
                res_gf[i] += np.abs(j_add[i, j]) / gj_sum[j] * (1 - r_base[j, j] / r_compr[j, j])
                grad_gf[i] += grad[j]
        # Create array with joint configuration suggestions
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
            li = self.__compute_inner_products(j_base=j_base, j_add=j_add, k=idx_to_add, nm=nm)
            li_accepted = True
            for i in range(len(li)):
                if li[i] >= self.__li_threshold:
                    li_accepted = False
            if li_accepted:
                indices_to_use.append(j_add_idx_dict[idx_to_add])
                added_indices += 1
            idx_rank += 1
        logging.info('LI: Skipping %d configurations', idx_rank - res_count)
        if grad_count > 0:
            grad_count += res_count - added_indices
            if len(sorted_indices_grad) > grad_count:
                indices_to_use = indices_to_use + list(j_add_idx_dict[sorted_indices_grad[0:grad_count]])
            else:
                indices_to_use = indices_to_use + list(j_add_idx_dict[sorted_indices_grad])
        return np.unique(indices_to_use)

    def init_scheme(self):
        """ Creates the initial measurement scheme.

        Creates an initial electrode setup with the selected electrode configuration type. Tries to use half of the
        electrodes when the electrode count is dividable by two.

        Returns:
            The scheme containing the initial electrode configurations.
        """
        electrode_count = np.ceil((self.__world_x - 2 * self.__electrode_offset) / self.__spacing) + 1
        # Try to use half of the electrodes
        if np.floor((electrode_count - 1) / 2) == (electrode_count - 1) / 2:
            electrode_count = (electrode_count - 1) / 2 + 1
        else:
            logging.info('Electrodes could not be divided in half for initial configuration! Using all electrodes!')
        electrodes = pg.utils.grange(start=self.__electrode_offset, end=self.__world_x-self.__electrode_offset,
                                     n=electrode_count)
        # Create initial scheme
        scheme = pb.createData(elecs=electrodes, schemeName=self.__base_configs[0])
        for i in range(1, len(self.__base_configs) - 1):
            scheme_tmp = pb.createData(elecs=electrodes, schemeName=self.__base_configs[i])
            scheme = schemeUtil.merge_schemes(scheme1=scheme, scheme2=scheme_tmp, tmp_dir=self.__folder_tmp)
        return scheme

    def update_scheme(self, old_scheme: pb.DataContainerERT, fop: pb.DCSRMultiElectrodeModelling, inv_grid: pg.Mesh,
                      inv_result: pg.RVector, iteration_subdir: str):
        """ Updates the used electrode configurations based on different criteria.

        Method that creates a new configuration scheme that extends the last used scheme with additional configurations
        computed by __compute_next_configs(...).

        Parameter:
            old_scheme: The currently used measurement scheme.
            fop: The forward operator, the last inversion used.
            inv_grid: The mesh used in the last inversion.
            inv_result: The resistivities on inv_grid.
            iteration_subdir: Subfolder to save files for debugging and testing purposes.

        Returns:
            The updated scheme.
        """
        self.__iteration = self.__iteration + 1
        # Create comprehensive scheme on first iteration
        if self.__comp_scheme == None:
            self.__create_comprehensive_scheme()
        # Compute next electrode configurations
        logging.info('Computing Jacobian for comprehensive scheme...')
        j_compr = self.__compute_jacobian(mesh=inv_grid, res=inv_result, scheme=self.__comp_scheme)
        logging.info('Computing goodness function...')
        config_indices = self.__compute_next_configs(scheme_base=old_scheme, scheme_compr=self.__comp_scheme,
                                                     j_base=pg.utils.base.gmat2numpy(fop.jacobian()), j_compr=j_compr,
                                                     mesh=inv_grid, cell_data=inv_result,
                                                     iteration_subdir=iteration_subdir)
        # Save added configurations to file
        outpath = self.__folder_tmp + '../' + iteration_subdir + 'configs_to_add.txt'
        logging.info('Saving computed configs to: ' + outpath)
        with open(outpath, 'w') as f:
            for i in range(len(config_indices)):
                f.write('%d\n' % (config_indices[i]))
            f.close()
        # Add new configurations to original scheme
        scheme_add = schemeUtil.extract_configs_from_scheme(scheme=self.__comp_scheme, config_indices=config_indices,
                                                            tmp_dir=self.__folder_tmp)
        return schemeUtil.merge_schemes(scheme1=old_scheme, scheme2=scheme_add, tmp_dir=self.__folder_tmp)
