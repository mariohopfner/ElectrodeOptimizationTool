#!/usr/bin/env python
from main.FlexibleInversionController import FlexibleInversionController
from main.SimpleRefiningElectrodeUpdater import SimpleRefiningElectrodeUpdater
from main.ResolutionElectrodeUpdater import ResolutionElectrodeUpdater
from util.InversionConfiguration import InversionConfiguration

config = InversionConfiguration(general_bert_verbose=True,
                                world_x=200, world_y=100, world_resistivities=[1000,50], world_gen='incl',
                                world_layers=[], world_angle=[],
                                world_inclusion_start=[20,-20], world_inclusion_dim=[50,30],
                                sim_mesh_quality=34, sim_noise_level=0.1, sim_noise_abs=1e-6, sim_schemes=['dd'],
                                inv_lambda=50, inv_para_dx=0.3, inv_max_cell_area=30,
                                finv_max_iterations=5, finv_max_spacing=20, finv_min_spacing=5)

electrode_updater = ResolutionElectrodeUpdater(config.world_x, config.finv_min_spacing, config.finv_max_spacing)

fic = FlexibleInversionController(config, electrode_updater)
fic.run()