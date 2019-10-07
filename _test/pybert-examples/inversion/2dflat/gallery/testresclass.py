import pybert as pb

res = pb.Resistivity('gallery.dat')
res.invert()
res.showResultAndFit()
# res.saveFigures()
