DCFEMLib->Examples->Inversion->2dFlat->Gallery
###############################################

This example represents a minimalistic 2d flat-earth field data profile for quick testing.
It was friendly provided by Folker Donner (University of Mining and Technology, Freiberg).
It is a very small profile over a known mining gallery that is used for dewatering of the underground mines.

Dipole-dipole measurements have been used, the data quality was very good.
Therefore the data error was estimated by 1% plus a voltage error of 50 microvolts (err column in data file).
The Input in the file gallery.dat is already the apparent resistivity as geometric factor is trivial.
The result shows a small but distinct high-resistivity anomaly besides another anomaly whose origin is not completely clear.

For running the inversion just call

bert gallery.cfg all

Show the result by (replace show by mkpdf to generate a pdf instead)

bert gallery.cfg show 

The result and all belonging files can be saved (into a result directory) by

bert gallery.cfg save 

There are two Python scripts to test the inversion with pybert.
The first (testpbinv.py) is a physics-level script setting up the forward operator and the inversion.
The second one (testresclass.py) uses the ready ERT manager class and is thus far more simple.
