#!/usr/bin/env python

import util.worldGenerator as wg
import util.schemeFileGenerator as sfg
import util.dataSimulator as ds

filename = sfg.create_scheme_file()
world = wg.generate_simple_layered_world(scheme_file=filename, layers=[-5,-30])
data = ds.simulate_data_from_world(world=world, scheme_file=filename, resistivities=[100, 300, 800])

print("")

#data.get("rhoa")
