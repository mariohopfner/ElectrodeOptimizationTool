DCFEMLib->Examples->Inversion->2dStruct
#######################################

This example shows how to add structural information such as reflectors from seismic or GPR.
It was measured and friendly provided by the K-UTec GmbH Sondershausen (thanks to T. Schicht).
Aim of the study was a bedrock detection that was carried out with resistivity and refraction seismics.
The velocity structure showed to be a very clear 2-layer case.
So the result (layer boundary) of the refraction study can serve as structural information.

The file bedrock.xz contains the course of the boundary as x-z pairs.
We now include this file into the configuration file using the INTERFACE option
INTERFACE=bedrock.xz
In order to compare the result with and without structure we call

> BertNew2d bedrock.dat > bert.cfg
> Bert bert.cfg all save
> echo INTERFACE=bedrock.xz >> bert.cfg
> bert bert.cfg all save

