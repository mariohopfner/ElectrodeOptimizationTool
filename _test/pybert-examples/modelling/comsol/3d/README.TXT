This example is about reading in a 3D geometry created and exported by Comsol as .mphtxt file.
The model is a 1x1x1 m cube with two layers, and a small 0.2x0.2x0.2 m block at the surface.
The python script reads in the vertices, the edges, the edge markers and the faces and prints out the corresponding edges.
Out of this the input for any mesh generator needs to be created.