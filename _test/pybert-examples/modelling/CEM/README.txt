Complete Electrode Model (CEM)
==============================

In geophysics, often electrodes are considered points on the surface of the modelling domain. However, for small-scale measurements or when using metal infrastructure, this assumtion is not accurate anymore. The complete electrode model (CEM) goes back to medical imaging (Cheng et al., in a small scale where the size of electrodes cannot be neglected. Rücker & Günther (2011) brought it to geophysical ERT imaging and presented several modelling examples that are provided here, following the idea of reproducible science. BERT is easily detecting extended CEM electrodes by face markers starting from -10000 downwards. So the only problem is to generate an appropriate mesh. From a computational perspective, it does not have to be as fine as with node electrodes. Mesh refinement is often controlled by the number of subfaces.

The examples in Rücker & Günther (2011) are ordered according to the Figure numbers:

Figure 3: accuracy - missing
----------------------------

Figure 4: Potential distribution high&low Z - missing
-----------------------------------------------------
good for general understanding

Figure 5: different electrode shapes - missing
----------------------------------------------
(less important for users)

Table 1: surface arrays - missing
---------------------------------
effect of stick electrodes on surface arrays
could be done with SEM more easily

Figures 6+7 + Table 2: tank measurements = tank
-----------------------------------------------
replacing screw electrodes by points in a model tank

Figure 8: plate electrodes - plate_electrodes
---------------------------------------------
using square plate electrodes (0.1-0.5m) on a surface array (a=1m)

Figure 9: line electrodes - line_electrodes
-------------------------------------------
simulating a capacatively coupled line electrodes (Ohmmapper)

Figure 10: Borehole electrode - borehole_electrode
--------------------------------------------------
using a borehole to inject current
a dipping plate is used as passive CEM body distorting current flow
measurement by point electrodes at the surface

Figure 11 and Table 3: ring_electrodes
--------------------------------------
Ring electrodes mounted on a borehole/direct-push tool
two different real instruments (a=0.25m and a=0.05m) simulated

Additional examples:

pad_electrodes: Circular pad electrodes on a rock sample

prismesh: CEM modelling of a borehole array using a prismatic mesh

SEM
===
An alternative and computationally less expensive method for elongated electrodes is the shunt electrode model (SEM) presented by Wang et al. (1999) for industrial process tomography and brought to geophysics by Ronczka et al. (2015).
See the SEM subfolder for some of the examples in the paper.

References
==========
Rücker, C. & Günther, T. (2011): The simulation of Finite ERT electrodes using the complete electrode model. - Geophysics 76(4), F227-238, doi:10.1190/1.3581356.

Cheng, K.-S., D. Isaacson, J. C. Newell, and D. G. Gisser, 1989, Electrode models for electric current computed tomography: IEEE Transactions on Biomedical Engineering, 36, no. 9, 918–924, doi:10.1109/10.35300.

Ronczka, M., Rücker, C. & Günther, T. (2015): Numerical study of long electrode electric resistivity tomography – Accuracy, sensitivity and resolution. Geophysics, 80(6), E317-328, doi:10.1190/geo2014-0551.1.

Wang, M., F. Dickin, and R. Mann, 1999, Electrical resistance tomographic sensing system for industrial applications: Chemical Engineering Communications, 175, 49–70, doi: 10.1080/00986449908912139.