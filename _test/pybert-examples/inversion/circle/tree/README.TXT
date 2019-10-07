This is an example for tree tomography friendly provided by Niels Hoffmann of
the HAWK Goettingen. It represents a data file where 24 electrodes have been
sticked around a hollow lime tree. As usual, dipole-dipole measurements were
taken. A simple cfg file can be obtained by

$ bertNew2dCirc hollow_limetree.ohm > bert.cfg

We additionally improved it by a denser mesh with equidistant boundary and a
higher quality. Additionally we used a slightly smaller regularization and the
blocky model option. The result can finally be compared to the tree cut image
hollow_limetree.jpg.
