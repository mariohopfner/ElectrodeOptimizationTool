# Geoelectrics in-field experimental design optimiziation
This code provides a basic concept of optimizing the actively used electrode sets in an experiment while still measuring.
The optimization algorithm is based on the concepts of Stummer et al., 2004 (https://doi.org/10.1190/1.1649381).
This software was created as a proof-of-concept and still lacks the ability to communicate with actual measurement devices which is needed for real world operation.
For simulation and inversion purposes, PyGIMLi (https://github.com/gimli-org/gimli) and pybert (https://gitlab.com/resistivity-net/bert) are used.

The following features are implemented:
* Generate synthetic scenarios with a small collection of generators
* Simulate a measurement with a variable set of electrodes
* Simultaneously measure and update the electrode configuration
* Automatically invert the measured data with customizable parameters

Dependencies:
* pygimli 1.0.11_0
* pybert 2.2.10_0

As this software is a basis for future development, many components are implemented modularly and can easily be replaced with alternative code (e.g. simulation and inversion libraries, electrode optimization criterion, ...).
Therefore, any changes and ideas are welcome.
Feel free to contact me for any questions or ideas!

## License notice
The ElectrodeOptimizationTool is distributed under the terms of the Apache 2.0 license, which can be found here: https://github.com/mariohopfner/ElectrodeOptimizationTool/blob/master/LICENSE.md
