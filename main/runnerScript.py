#!/usr/bin/env python
import numpy as np

from main.FlexibleInversionController import FlexibleInversionController
from main.ResolutionElectrodeUpdater import ResolutionElectrodeUpdater
from main.InversionConfiguration import InversionConfiguration

# Set up inversion parameter
config = InversionConfiguration(general_bert_verbose=True,
                                general_folder_suffix='-incl',
                                world_x=200, world_z=100, world_resistivities=[100,10], world_gen='incl',
                                world_layers=[], world_angle=0,
                                world_inclusion_start=[20, -10], world_inclusion_dim=[5, 5],
                                world_tile_x=30, world_tile_z=5,
                                world_electrode_offset=0,
                                sim_mesh_quality=34, sim_mesh_maxarea=30, sim_noise_level=5, sim_noise_abs=1e-6,
                                inv_lambda=10, inv_dx=4, inv_dz=4, inv_depth=50,
                                inv_final_lambda=60, inv_final_dx=2, inv_final_dz=2, inv_final_depth=50,
                                finv_max_iterations=25, finv_spacing=2, finv_base_configs=['slm'],
                                finv_add_configs=['dd', 'wb', 'pp', 'pd', 'wa', 'hw', 'gr'],
                                finv_gradient_weight=0, finv_addconfig_count=50, finv_li_threshold=0.95)

# initialize electrode updater
electrode_updater = ResolutionElectrodeUpdater(world_x=config.world_x, spacing=config.finv_spacing,
                                               electrode_offset=config.world_electrode_offset,
                                               base_configs=config.finv_base_configs,
                                               add_configs=config.finv_add_configs,
                                               gradient_weight=config.finv_gradient_weight,
                                               addconfig_count=config.finv_addconfig_count,
                                               li_threshold=config.finv_li_threshold)

# start synthetic optimized inversion iteration
fic = FlexibleInversionController(config, electrode_updater)
fic.run()