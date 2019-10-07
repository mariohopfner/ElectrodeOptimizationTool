This is a crosshole tomography problem, provided by O.Kuras from the British
Geological Survey (BGS) out of the ALERT project. It represents about 1300 data
obtained by crosshole measurement between 5 very shallow (0-1.6m) boreholes.

We use the command introduced by PARAGEOMETRY="polyFlatPara 2dxh.ohm'
into the cfg file, which calculates the inversion box automatically.
Additionally we set a pretty good quality for the parameter mesh PARA2DQUALITY=34.5.
Additionally we use PARADX=0.05 in order to insert a node between 2 electrodes.

In the subdirectories free and reg two other parameterization strategies are used:
1) an unstructured triangular mesh without electrodes as nodes
2) a regular mesh with electrodes on nodes or not

After the normal inversion we would like to do a time lapse inversion.
We unpack 2dxh-timelapse.zip into the directory providing 35 data files *.dat
and a timeseries data file timesteps.txt, which we put into inv.cfg by
TIMESTEPS=timesteps.txt
A run of the inversion and visualization (calc show) will create many files
showmodel.*.vtk with the absolute results and diff_*.vtk with differences, which
can be read into paraview and scrolled through time using the time slider.
