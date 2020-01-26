#!/usr/bin/env python
from main.FlexibleInversionController import FlexibleInversionController
from main.SimpleRefiningElectrodeUpdater import SimpleRefiningElectrodeUpdater
from main.ResolutionElectrodeUpdater import ResolutionElectrodeUpdater
from util.InversionConfiguration import InversionConfiguration

gradient_weights = [1]

for i in range(len(gradient_weights)):
    config = InversionConfiguration(general_bert_verbose=True,
                                    world_x=200, world_y=100, world_resistivities=[1000,50], world_gen='incl',
                                    world_layers=[], world_angle=0,
                                    world_inclusion_start=[30,-20], world_inclusion_dim=[20,10],
                                    sim_mesh_quality=34, sim_noise_level=0.2, sim_noise_abs=1e-6,
                                    inv_lambda=100, inv_para_dx=0.2, inv_max_cell_area=25,
                                    finv_max_iterations=8, finv_spacing=5, finv_base_configs=['dd'],
                                    finv_add_configs=['wa', 'wb', 'pp', 'pd', 'slm', 'hw', 'gr'],
                                    finv_gradient_weight=gradient_weights[i], finv_addconfig_count=100)

    electrode_updater = ResolutionElectrodeUpdater(config.world_x, config.finv_spacing,
                                                   config.finv_base_configs, config.finv_add_configs,
                                                   config.finv_gradient_weight)

    fic = FlexibleInversionController(config, electrode_updater)
    fic.run()