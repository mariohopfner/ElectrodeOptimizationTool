DCFEMLib->Examples->Inversion->2dFlat->Gallery
###############################################

This example was measured by the Leibniz Institute for Applied Geosciences, Hannover by T. Günther and W. Südekum.
Its aim was to delineate sedimentation structures beneath the Feldungel lake near Osnabrueck.
Electrodes have been spread out from one shore on the lake bottom onto the other shore.
The spacing was 2m and a combination of Wenner-alpha and Wenner-beta was applied.
Since the lake resistivity is known (22.5 Ohmm) this is excluded from inversion hand:
1. We put the electrode positions (from 0 to -2.6m height) and resistances into the input file
2. We start as for a topographic case and generate the meshing input
invert inv.cfg domain
3. As a result we obtain the poly file mesh/mesh.poly which we copy to mymesh.poly
4. We need to add the water surface by an edge between the left and the right shore 
   A view into the poly file that these are represented by the points 3 and 138
   So add another edge at the end of the edges (line 303) by inserting
   151 3 138 -1
   and increase the number of edges in line 152 from 151 to 152
5. Finally we add a region marker somewhere in the lake with marker 1 (not inverted) at the end
   2 50 -1 1 0.0
   and increase the number of regions from 2 to 3
   (see triangle home page for description of triangle poly files).

We use this altered poly file in the inversion by introducing into the cfg file
PARAGEOMETRY=mymesh.poly
Furthermore we add the following options
TOPOGRAPHY=0     # ensures that the primary potentials are really analytic
RHOSTART=22.5    # Start(=background) resistivity
SURFACESMOOTH=0  # prevent smoothing (edge swapping possible)

Note that the latter options will be obsolete in dcfemlib2 due to automatisms and the region technique.
The other options we use are:
ZWEIGHT=0.2       # enhances layered (sediment) structures
OVERRIDEERROR=1  # do not take the measured errots in file (too optimistic), but:
INPUTERRLEVEL=2       # 2% plus
INPUTERRVOLTAGE=20e-6 # 20 microvolts
