import pygimli as g
import pylab as P

# reference solution
Ref = g.DataContainer( 'out.ohm' )
r0 = Ref( 'r' )
# individual solutions
names = [ 'H1', 'H2', 'H3', 'P2', 'H2P2' ]
Data = []
for name in names:
    # read in file and append modeled resistance
    filename = 'out' + name + '.ohm'
    ohm = g.DataContainer( filename )
    Data.append( g.RVector( ohm('r') ) ) # append a copy

# print out results
print("Name     min   max   mean  std   rrms")
for i, ri in enumerate( Data ):
    dR = ri / r0 * 100. - 100. # difference in per cent
    nums = P.array( [ g.min(dR), g.max(dR), g.mean(dR), P.std( dR ), g.rrms( r0, ri ) * 100. ] )
    print("%6s" % names[i], nums.round(2))

# read in comsol result and according measurement
Comsol = g.DataContainer( 'comsol.dat' )
Data150 = g.DataContainer( 'data150.ohm' )

# read in Comsol computation and compare with BERT solution
rComsol = Comsol('r') / 20. # was done with 20 Ohmm
rBERT = Data150('r')
dR = rComsol / rBERT * 100. - 100.
nums = P.array( [ g.min(dR), g.max(dR), P.mean(dR), P.std( dR ), g.rrms( rBERT , rComsol ) * 100. ] )
print("Comsol", nums.round(2))