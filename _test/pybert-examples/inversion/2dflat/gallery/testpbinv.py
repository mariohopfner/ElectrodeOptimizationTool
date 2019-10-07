import pygimli as pg
import pybert as pb
from pygimli.meshtools import createParaMesh


data = pb.DataContainerERT('gallery.dat')

mesh = createParaMesh(data.sensorPositions(), paraDX=0.5, paraDepth=10,
                      paraBoundary=10, boundary=4.4, quality=34.5)
# pg.show(mesh, mesh.cellMarkers())

rhoa = data('rhoa') * 1.0  # might come from another file or modelling
f = pb.DCSRMultiElectrodeModelling(mesh, data)  # DC res with sing. removal
f.region(1).setBackground(True)  # background prolongation
f.region(2).setStartValue(pg.median(rhoa))
   
f.createRefinedForwardMesh(True)
tLog = pg.RTransLog()

INV = pg.RInversion(rhoa, f, tLog, tLog, True)
INV.setRelativeError(data('err'))  # alternatively a constant number (0.02)
res = INV.run()
pd = f.regionManager().paraDomain()
pg.show(pd, res, colorBar=True)
print((min(res), max(res)))
pd.addExportData('resistivity', res)
f.regionManager().paraDomain().exportVTK('galleryTmp')
