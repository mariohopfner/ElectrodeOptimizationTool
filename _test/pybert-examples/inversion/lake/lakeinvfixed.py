import pygimli as pg
import pybert as pb
# from pygimli.meshtools import createParaMesh


data = pb.DataContainerERT('feldungel.data')
data.set('err', pg.RVector(data.size(), 0.02))
mesh = pg.Mesh('mesh/mesh.bms')

f = pb.DCSRMultiElectrodeModelling(mesh, data)  # DC res with sing. removal
#f.setPrimaryPotFileBody('primaryPot/pot_s.bmat')
f.region(1).setBackground(True)  # background prolongation
# f.region(3).setBackground(True)  # not necessary
f.region(3).setFixValue(22.5)
f.region(2).setStartValue(pg.median(data('rhoa')))

f.createRefinedForwardMesh(True)
tLog = pg.RTransLog()

INV = pg.RInversion(data('rhoa'), f, tLog, tLog, True)
INV.setRelativeError(data('err'))  # alternatively a constant number (0.02)
INV.setLambda(20)
res = INV.run()
pg.show(f.regionManager().paraDomain(), res, colorBar=True)
