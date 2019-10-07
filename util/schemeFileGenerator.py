#!/usr/bin/env python

import numpy as np
import itertools as itt

# TODO implement dynamic decimals with electrode_accuracy
'''
Functions that writes a pybert scheme file for electrode configurations on a simple 2D line
    :parameter
        name               - name of the output file
        x_min              - first x coordinate with an electrode
        x_max              - furthest x coordinate with an electrode
        nel                - number of electrodes distributed on the surface
        electrode_accuracy - count of decimals for electrode spacing accuracy
'''
def create_scheme_file(name="test.shm", x_min=0, x_max=100, nel=11, electrode_accuracy=2):

    # create file reference
    file = open(name, "w")

    # write electrodes header
    file.write(str(nel))
    file.write("\n# x y z\n")

    # compute and write electrode positions
    electrode_ids = np.linspace(1,nel,nel)
    for i in electrode_ids:
        x = (i-1)*np.round(x_min+(x_max-x_min)/(nel-1),electrode_accuracy)
        out = "{:.2f} {}\n".format(
            x,
            "0 0")
        file.write(out)

    # compute all possible configurations
    configurations = list(itt.combinations(electrode_ids, 4))

    # write configurations header
    file.write(str(len(configurations)))
    file.write("\n# a b m n\n")

    # write configurations
    for c in configurations:
        out = "{:d} {:d} {:d} {:d}\n".format(
            int(c[0]),
            int(c[1]),
            int(c[2]),
            int(c[3]))
        file.write(out)

    # write an empty topography
    file.write("0\n")

    # close file stream
    file.close()

    return name