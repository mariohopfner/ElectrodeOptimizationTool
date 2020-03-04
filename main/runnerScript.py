#!/usr/bin/env python

from main.FlexibleInversionController import FlexibleInversionController
from main.ResolutionElectrodeUpdater import ResolutionElectrodeUpdater
from main.InversionConfiguration import InversionConfiguration

spacings = [2]

for i in range(len(spacings)):
    config = InversionConfiguration(general_bert_verbose=True, general_folder_suffix='-debugtests',
                                    world_x=200, world_z=100, world_resistivities=[10, 100], world_gen='incl',
                                    world_layers=[], world_angle=0,
                                    world_inclusion_start=[50,-20], world_inclusion_dim=[20,10],
                                    world_tile_x=40, world_tile_z=5,
                                    world_electrode_offset=0,
                                    sim_mesh_quality=34, sim_mesh_maxarea=30, sim_noise_level=5, sim_noise_abs=1e-6,
                                    inv_lambda=10, inv_dx=10, inv_dz=10, inv_depth=50,
                                    inv_final_lambda=50, inv_final_dx=2, inv_final_dz=2, inv_final_depth=50,
                                    finv_max_iterations=5, finv_spacing=2, finv_base_configs=['dd'],
                                    finv_add_configs=['wa', 'wb', 'pp', 'pd', 'slm', 'hw', 'gr'],
                                    finv_gradient_weight=0, finv_addconfig_count=100, finv_li_threshold=0.8)

    electrode_updater = ResolutionElectrodeUpdater(world_x=config.world_x, spacing=config.finv_spacing,
                                                   electrode_offset=config.world_electrode_offset,
                                                   base_configs=config.finv_base_configs,
                                                   add_configs=config.finv_add_configs,
                                                   gradient_weight=config.finv_gradient_weight,
                                                   addconfig_count=config.finv_addconfig_count,
                                                   li_threshold=config.finv_li_threshold)

    fic = FlexibleInversionController(config, electrode_updater)
    fic.run()