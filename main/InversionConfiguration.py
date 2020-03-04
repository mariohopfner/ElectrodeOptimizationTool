class InversionConfiguration:
    """A utility class for storing all inversion options at the same place

    This class is mainly used for configuring the FlexibleInversionControllers behaviour. Should be passed to the FIC
    init method.

    Parameter:
        general_bert_verbose: A boolean indicating if bert should print verbose information.
        general_folder_suffix: A string extending the job-specific folder name, e.g. '-test'.
        world_x: A float describing the simulation worlds x dimension.
        world_z: A float describing the simulation worlds z dimension.
        world_resistivities: A list of floats describing the simulation worlds regions resistivities.
        world_gen: A string describing the used simulation world generator.
        world_layers: A list of floats describing the depths of layers in the simulation world. Only used when the
                      world generator 'lay' is used.
        world_angle: A float describing the angle at which the layers of the simulation world are passing through the
                     world. Only used when the world generator 'lay' is used.
        world_inclusion_start: A list containing two floats setting the upper left x and y coordinates of the inclusion
                               in the simulation world. The y-attribute should be >= 0. Only used when the world
                               generator 'incl' is used.
        world_inclusion_dim: A list containing two floats setting the x and y dimensions of the inclusion in the
                             simulation world. Only used when the world generator 'incl' is used.
        world_tile_x: A float setting the x dimension size of a single tile.
        world_tile_z: A float setting the z dimension size of a single tile.
        world_electrode_offset: A float indicating the offset between the world boundary and the outermost electrodes.
        sim_mesh_quality: An int describing the mesh quality used for simulation. Passed to the PyGimli meshtools.
        sim_mesh_maxarea: A float describing the maximum area of a mesh cell for data simulation.
        sim_noise_level: A float describing the simulation noise level. Passed to the PyBert simulator.
        sim_noise_abs: A float describing the absolute simulation noise. Passed to the PyBert simulator.
        inv_lambda: A float describing the regularization lambda. Passed to the PyBert inverter.
        inv_dx: A float describing the inversion mesh X dimension cell size.
        inv_dz: A float describing the average inversion mesh Z dimension cell size.
        inv_depth: A float setting the maximum depth of the inversion model.
        inv_final_lambda: A float describing the regularization lambda of the final inversion. Passed to the PyBert
                          inverter.
        inv_final_dx: A float describing the inversion final mesh X dimension cell size.
        inv_final_dz: A float describing the average final inversion mesh Z dimension cell size.
        inv_final_depth: A float setting the maximum depth of the final inversion model.
        finv_max_iterations: An int setting the maximum iterations the flexible inversion shall run.
        finv_spacing: A float describing the electrode spacing within the world.
        finv_base_configs: A list of strings describing the configuration short-terms used as initial configuration
                           sets.
        finv_add_configs: A list of strings describing the configuration short-terms used as updating configuration
                          sets.
        finv_gradient_weight: A float describing the weight of the gradient in relation to the goodness function.
                              Gradient calculation will be deactivated if this value is 0. Should be >= 0.
        finv_addconfig_count: An int describing the configuration count added per iteration.
        finv_li_threshold: A float indicating the maximum value the li function of a configuration is allowed to have to
                           be still accepted.

    Typical usage example:
      config = InversionConfiguration(...)
      fic = FlexibleInversionController(config: config, electrode_updater: ...)
    """
    def __init__(self,
                 general_bert_verbose: bool, general_folder_suffix: str,
                 world_x: float, world_z: float, world_resistivities: list, world_gen: str, world_layers: list,
                 world_angle: float, world_inclusion_start: list, world_inclusion_dim: list, world_tile_x: float,
                 world_tile_z: float, world_electrode_offset: float,
                 sim_mesh_quality: int, sim_mesh_maxarea: float, sim_noise_level: float, sim_noise_abs: float,
                 inv_lambda: float, inv_dx: float, inv_dz: float, inv_depth: float,
                 inv_final_lambda: float, inv_final_dx: float, inv_final_dz: float, inv_final_depth: float,
                 finv_max_iterations: int, finv_spacing: float, finv_base_configs: list, finv_add_configs: list,
                 finv_gradient_weight: float, finv_addconfig_count: int, finv_li_threshold: float):
        # General parameter
        self.general_bert_verbose = general_bert_verbose
        self.general_folder_suffix = general_folder_suffix
        # World parameter
        self.world_x = world_x
        self.world_z = world_z
        self.world_resistivities = world_resistivities
        self.world_gen = world_gen    # incl, lay, tile
        self.world_electrode_offset = world_electrode_offset
        # Layered world parameter
        self.world_layers = world_layers
        self.world_angle = world_angle
        # Homogeneous world with inclusion parameter
        self.world_inclusion_start = world_inclusion_start
        self.world_inclusion_dim = world_inclusion_dim
        #
        # Tiled world parameter
        self.world_tile_x = world_tile_x
        self.world_tile_z = world_tile_z
        # Simulation parameter
        self.sim_mesh_quality = sim_mesh_quality
        self.sim_mesh_maxarea = sim_mesh_maxarea
        self.sim_noise_level = sim_noise_level
        self.sim_noise_abs = sim_noise_abs
        # Inversion parameter
        self.inv_lambda = inv_lambda
        self.inv_dx = inv_dx
        self.inv_dz = inv_dz
        self.inv_depth = inv_depth
        # Final inversion parameter
        self.inv_final_lambda = inv_final_lambda
        self.inv_final_dx = inv_final_dx
        self.inv_final_dz = inv_final_dz
        self.inv_final_depth = inv_final_depth
        # Flexible inversion parameter
        self.finv_max_iterations = finv_max_iterations
        self.finv_spacing = finv_spacing
        self.finv_base_configs = finv_base_configs
        self.finv_add_configs = finv_add_configs
        self.finv_gradient_weight = finv_gradient_weight
        self.finv_addconfig_count = finv_addconfig_count
        self.finv_li_threshold = finv_li_threshold

    def check_integrity(self) -> int:
        """Checks the configuration objects integrity.

        Checks the integrity of the configuration object by validating variable types, lengths and inter-variable
        relationships.

        Returns:
            Whether the configuration object is integer (0) or there are validation errors (error code).
        """
        if isinstance(self.world_x,list) or isinstance(self.world_z, list):
            return 1

        if not isinstance(self.world_resistivities, list):
            return 2

        if self.world_gen != 'incl' and self.world_gen != 'lay' and self.world_gen != 'tile':
            return 3

        if self.world_gen == 'incl':
            if not isinstance(self.world_inclusion_start,list) or not isinstance(self.world_inclusion_dim,list):
                return 4
            if len(self.world_inclusion_start) != 2 or len(self.world_inclusion_dim) != 2:
                return 4
        if self.world_gen == 'lay':
            if not isinstance(self.world_layers, list):
                return 5
            if isinstance(self.world_angle, list):
                return 5
        if self.world_gen == 'tile':
            if isinstance(self.world_tile_x,list) or isinstance(self.world_tile_z, list):
                return 6

        if isinstance(self.world_electrode_offset, list):
            return 7

        if isinstance(self.sim_mesh_quality,list) or isinstance(self.sim_noise_level, list) \
                or isinstance(self.sim_noise_abs, list) or isinstance(self.sim_mesh_maxarea, list):
            return 8

        if isinstance(self.inv_lambda,list) or isinstance(self.inv_dx, list) \
                or isinstance(self.inv_dz, list) or isinstance(self.inv_depth, list):
            return 9

        if isinstance(self.finv_max_iterations, list):
            return 10

        if isinstance(self.finv_spacing, list):
            return 11

        if not isinstance(self.finv_base_configs, list) or not isinstance(self.finv_add_configs, list):
            return 12

        if isinstance(self.finv_gradient_weight, list):
            return 13

        if isinstance(self.finv_addconfig_count, list):
            return 14

        if isinstance(self.finv_li_threshold, list):
            return 15

        return 0

    def print_config(self) -> list:
        """Creates a string list with configuration parameters

        Creates a string list containing all configuration parameters in a readable manner. Can be used for archiving
        the configuration parameters line by line.

        Returns:
            A list of strings containing the configuration parameters and a small description.
            Example: ['Bert Verbose: True','World X: 200', ...]
        """
        conf_string = ['Bert Verbose: ' + str(self.general_bert_verbose),
                       'Folder suffix: ' + str(self.general_folder_suffix), 'World X: ' + str(self.world_x),
                       'World Z: ' + str(self.world_z), 'World resistivities: ' + str(self.world_resistivities),
                       'World generator: ' + str(self.world_gen)]

        if self.world_gen == 'lay':
            conf_string.append('World layers: ' + str(self.world_layers))
            conf_string.append('World angle: ' + str(self.world_angle))

        if self.world_gen == 'incl':
            conf_string.append('World inclusion start: ' + str(self.world_inclusion_start))
            conf_string.append('World inclusion dimension: ' + str(self.world_inclusion_dim))

        if self.world_gen == 'tile':
            conf_string.append('World tile size X: ' + str(self.world_tile_x))
            conf_string.append('World tile size Z: ' + str(self.world_tile_z))

        conf_string.append('Electrode offset: ' + str(self.world_electrode_offset))

        conf_string.append('Mesh quality: ' + str(self.sim_mesh_quality))
        conf_string.append('Mesh max area: ' + str(self.sim_mesh_maxarea))
        conf_string.append('Noise level: ' + str(self.sim_noise_level))
        conf_string.append('Absolute noise: ' + str(self.sim_noise_abs))

        conf_string.append('Lambda: ' + str(self.inv_lambda))
        conf_string.append('Inv DX: ' + str(self.inv_dx))
        conf_string.append('Inv DZ: ' + str(self.inv_dz))
        conf_string.append('Inv Depth: ' + str(self.inv_depth))

        conf_string.append('Final Inv Lambda: ' + str(self.inv_final_lambda))
        conf_string.append('Final Inv DX: ' + str(self.inv_final_dx))
        conf_string.append('Final Inv DZ: ' + str(self.inv_final_dz))
        conf_string.append('Final Inv Depth: ' + str(self.inv_final_dz))

        conf_string.append('Max inversion counts: ' + str(self.finv_max_iterations))
        conf_string.append('Electrode spacing: ' + str(self.finv_spacing))
        conf_string.append('Base configs: ' + str(self.finv_base_configs))
        conf_string.append('Additional configs: ' + str(self.finv_add_configs))
        conf_string.append('Gradient weight: ' + str(self.finv_gradient_weight))
        conf_string.append('Configs to add: ' + str(self.finv_addconfig_count))
        conf_string.append('Inner products threshold: ' + str(self.finv_li_threshold))

        return conf_string