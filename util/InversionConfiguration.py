#!/usr/bin/env python

class InversionConfiguration:
    def __init__(self,
                 general_bert_verbose,
                 world_x, world_y, world_resistivities, world_gen, world_layers, world_angle,
                 world_inclusion_start, world_inclusion_dim,
                 sim_mesh_quality, sim_noise_level, sim_noise_abs, sim_schemes,
                 inv_lambda, inv_para_dx, inv_max_cell_area,
                 finv_max_iterations, finv_max_spacing, finv_min_spacing):
        # general params
        self.general_bert_verbose = general_bert_verbose

        # world params
        self.world_x = world_x
        self.world_y = world_y
        self.world_resistivities = world_resistivities
        self.world_gen = world_gen    # incl, lay
        # layered world
        self.world_layers = world_layers
        self.world_angle = world_angle
        # homogeneous world with inclusion
        self.world_inclusion_start = world_inclusion_start
        self.world_inclusion_dim = world_inclusion_dim

        # simulation params
        self.sim_mesh_quality = sim_mesh_quality
        self.sim_noise_level = sim_noise_level
        self.sim_noise_abs = sim_noise_abs
        self.sim_schemes = sim_schemes

        # inversion params
        self.inv_lambda = inv_lambda
        self.inv_para_dx = inv_para_dx
        self.inv_max_cell_area = inv_max_cell_area

        # flexible inversion params
        self.finv_max_iterations = finv_max_iterations
        self.finv_max_spacing = finv_max_spacing
        self.finv_min_spacing = finv_min_spacing

    def check_integrity(self):
        # checking that world dimensions are scalar
        if isinstance(self.world_x,list) or isinstance(self.world_y, list):
            return 1

        # checking that resistivities are not scalar
        if not isinstance(self.world_resistivities, list):
            return 2

        # checking that the world generator identifier is valid
        if self.world_gen != "incl" and self.world_gen != "lay":
            return 3

        # checking that generator specific attributes are given and valid
        if self.world_gen == "incl":
            if not isinstance(self.world_inclusion_start,list) or not isinstance(self.world_inclusion_dim,list):
                return 4
            if len(self.world_inclusion_start) != 2 or len(self.world_inclusion_dim) != 2:
                return 4
        if self.world_gen == "lay":
            if not isinstance(self.world_layers, list):
                return 5
            if isinstance(self.world_angle, list):
                return 6

        # checking that mesh quality and noise is scalar
        if isinstance(self.sim_mesh_quality,list) or isinstance(self.sim_noise_level, list) \
                or isinstance(self.sim_noise_abs, list):
            return 7

        # checking that schemes are stored in a list
        if not isinstance(self.sim_schemes, list):
            return 8

        # checking that inversion params are stored scalar
        if isinstance(self.inv_lambda,list) or isinstance(self.inv_para_dx, list) \
                or isinstance(self.inv_max_cell_area, list):
            return 9

        # checking that the max iterations are scalar
        if isinstance(self.finv_max_iterations, list):
            return 10

        # checking that electrode spacing is scalar
        if isinstance(self.finv_max_spacing, list) or isinstance(self.finv_min_spacing, list)\
                or self.finv_max_spacing < self.finv_min_spacing:
            return 11

        # configuration file integer
        return 0

    def print_config(self):
        conf_string = ["Bert Verbose: " + str(self.general_bert_verbose), "World X: " + str(self.world_x),
                       "World Y: " + str(self.world_y), "World resistivities: " + str(self.world_resistivities),
                       "World generator: " + str(self.world_gen)]

        if self.world_gen == "lay":
            conf_string.append("World layers: " + str(self.world_layers))
            conf_string.append("World angle: " + str(self.world_angle))

        if self.world_gen == "incl":
            conf_string.append("World inclusion start: " + str(self.world_inclusion_start))
            conf_string.append("World inclusion dimension: " + str(self.world_inclusion_dim))

        conf_string.append("Mesh quality: " + str(self.sim_mesh_quality))
        conf_string.append("Noise level: " + str(self.sim_noise_level))
        conf_string.append("Absolute noise: " + str(self.sim_noise_abs))
        conf_string.append("Simulation schemes: " + str(self.sim_schemes))

        conf_string.append("Lambda: " + str(self.inv_lambda))
        conf_string.append("Para DX: " + str(self.inv_para_dx))
        conf_string.append("Max Cell Area: " + str(self.inv_max_cell_area))

        conf_string.append("Max inversion counts: " + str(self.finv_max_iterations))
        conf_string.append("Min electrode spacing: " + str(self.finv_min_spacing))
        conf_string.append("Max electrode spacing: " + str(self.finv_max_spacing))

        return conf_string