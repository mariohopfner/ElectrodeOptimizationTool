Examples and Tutorials for the Boundless electrical resistivity tools (BERT)

These examples are for modelling purposes only. 
You need basic knowledge in shell scripting either for linux systems or for msys shell in windows. 
Start with the first example to become familiar to the syntax and the generally modelling approach.

1. 3d-halfspace-homogeneous
    3D Homogeneous half space with a four point measurement 
    This is the most basic tutorial and the 'must-read-first' part since its covers all basic concepts in deep detail.
    # TODO: python way -> sphinx-it

2. 2d-halfspace-two-layer
    2D two layered earth
    # TODO: total and secondary field calculation, semi analytical 1d reference solution (dc1dinv -m)
    # TODO: python way -> sphinx-it

3. 3d-modeltank
    Simple experimental tank in 3d

4. 3d-topography
    Calculate topography effect of a measurement with topography based on an elevation model

5. 3d-inside-horizontal-borehole
    Calculate geometric factors for measurement inside a horizontal borehole, e.g., mining gallery

6. 3d-halfspace-tensor
    Calculate response of tensor shape measurement on homogeneous a half space with a cubic heterogeneity

7. 2d-halfspace-ip
    like 2. but with a rectangular heterogeneity and complex resistivities.

A. CEM/
    Modelling with the complete electrode model (CEM), based on Rücker&Günther (2011)

    TODO

B. SEM
    Modelling with the shunt electrode model (SEM), based on Ronczka et al. (2015)
    
C. comsol/
    - Some tests to export the 2D/3D geometries created with Comsol multiphysics GUI that can be read by python (TODO is there a better place for this?)

    comsol/mesh3d
        Comparision of some results from comsol with BERT simulations (TODO needs review)

# ----- TODO -------
Alte Beispiele aus dcfemlib/examples/modelling checken/aufräumen und einpflegen

- Examples from paper: Part1 
    Halbraum/DX
    Geschichteter Halbraum mit Total/Secondary Potential
    Halbkugel
    Merapi?->Vogelsberg(s.o.)
    Gallery

- CEM-Beispiele aus Elektrodenpaper
- Prüfen ob manche Inversion Howtos nicht hier rein passen (tilted borehole)
- Examples from paper: CEM
- 2D topography from electrode positions
- A hollow tree
