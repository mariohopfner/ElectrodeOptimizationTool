BERT/DCFemLib->Examples->Inversion
#############################

Here are several small&fast but instructive examples for the inversion with BERT 1.
Aim of this assembly is to 
1) give an introduction to new BERT users
2) check inversion after code change for proper convergence
3) compare runtime for code improvements
4) compare with GIMLi::dcinv (BERT 2)
All data sets are field data and should always be fitted to values of about 1 (perfect) to 5.
Most of them should be working well with standard options (invertNew* datafile > inv.cfg).
But for some of them improved results can be achieved using 
- alternative regularisation parameters
- lower or upper resistivity bounds
- anisotropic weighting in order to obtain more lateral structures
- a finer model or a greater model depth

The suggested order of working through is:
1. 2dflat  - Surface measurements on flat earth
2. 2dtopo  - Surface measurements with topography
3. 2dxh - Crosshole measurements (with time lapse data)
4. 2dstruct - 2d inversion with structural constraints
5. 2dwater - Underwater survey using a sophisticated model
6. 3dflat  - 3d measurements without topography
7. 3dtopo  - 3d measurements on topography
8. 3dxh - 3d crosshole measurements
9. circle  - 2d measurements on closed geometry
10.3dtank - 3d measurements on closed geometry (with time lapse data)
