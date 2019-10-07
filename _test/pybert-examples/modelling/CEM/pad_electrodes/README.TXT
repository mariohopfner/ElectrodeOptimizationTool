Similar to the plate electrode example (Rücker & Günther, 2011), this example represents a four-point measurement on a small rock sample using circular pad electrodes as known from cardiograms. 

A 10x6x3cm wide box is created and shifted so that the four 2cm spaced electrodes are starting in the origin towards x direction.
The pad itself is created by the Python function createCircle (2D) which is then brought into 3D using createHull before it is added using the bash function polyScriptAddCEM imported from polyScripts.sh.
After meshing and running dcmod on a homogeneous half-space one can observe that there is a deviation of factor 2 compared to analytical flat-earth geometric factors, increasing for Wenner-beta and decreasing for Wenner-alpha.

References:
Rücker, C. & Günther, T. (2011) The simulation of finite ERT electrodes using the complete electrode model. Geophysics, 76, F227.