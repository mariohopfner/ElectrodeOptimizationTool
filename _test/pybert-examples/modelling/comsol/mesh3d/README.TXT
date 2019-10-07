This example is about a deposit body and comparing Comsol modelling results with BERT.
We read an already created mesh, where nodes and triangles have been exported as text.
The original mesh is saved as bms/vtk and refined spatially and polynomially with
different refinement levels.
As a reference, the surface of the mesh is extracted as PLC, the electrodes are added,
refined by 1/10 minimum spacing and with quadratic shape functions, the usual BERT way.

To run this example:

0. create meshes (mymesh*.bms) and PLC (mysurface.poly) from tri.txt und node.txt:

> python convertmymesh.py

1. create reference mesh (a/10 plus quadratic shape functions) from mysurface.poly

> sh mkmeshes.sh

2. perform modelling with various meshes (reference,H2,P2,H3,H2P2)

> sh docalc.sh

3. compare results by calculating RRMS values

> python cmpresults.py

Files:
    README.TXT
    
    cmpresults.py
    
    comsol.dat
    
    convertmymesh.py
    
    data.shm
    
    data150.shm
    
    docalc.sh
    
    electrodes.xyz
    
    mkmeshes.sh
    
    node.txt

    tri.txt