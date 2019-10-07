Shunt Electrode Model (SEM)
===========================

In geophysics, often electrodes are considered points on the surface of the modelling domain. However, sometimes this assumtion is not accurate anymore. The complete electrode model (CEM) presented by Rücker & Günther (2011) demonstrates how facial electrodes can be discretized to distribute current injection. Besides current distribution it shunts the electrode nodes so that the potentials are connected by a low conductance. This is also the idea of the Shunt Electrode Model (SEM) presented by Ronczka et al. (2015), which is particularly useful for elongated line electrodes. The paper presents modelling and inversion studies for using long steel-cased boreholes as ERT electrodes. Similar to CEM, markers starting from -10000 downwards are used to identify the electrode nodes that are to be connected. So again it is all about the mesh generation.

From the examples we chose a set covering all aspects, ordered according to the Figures in Ronczka et al. (2015):

Figure 2: fig02-comparison
Comparison of current density from SEM, CEM and CCM models

Figure 4: fig04-potentialcurrent
potential distribution and current density

Figure 6: fig06-sensitivity
sensitivity plots

Figure 7: fig07-arraycomparison
array comparison for rising saltwater body

Figure 10: fig10-inversion
3D inversion and resolution with differently long electrodes

References
==========
Ronczka, M., Rücker, C. & Günther, T. (2015): Numerical study of long electrode electric resistivity tomography – Accuracy, sensitivity and resolution. Geophysics, 80(6), E317-328, doi:10.1190/geo2014-0551.1.

Rücker, C. & Günther, T. (2011): The simulation of Finite ERT electrodes using the complete electrode model. - Geophysics 76(4), F227-238, doi:10.1190/1.3581356.
