import pygimli as g
import pybert as b
import pylab as P

H0 = b.DataMap('hom0.collect')
H1 = b.DataMap('hom1.collect')
I0 = b.DataMap('inhom0.collect')
I1 = b.DataMap('inhom1.collect')

data = b.DataContainerERT( 'cpp.shm' )

rhoa0 = P.asarray( I0.data(data) / H0.data(data) )
rhoa1 = P.asarray( I1.data(data) / H1.data(data) )

x = P.array( [data.sensorPosition(i).x() for i in range(1,20)] )

P.figure(1)
P.clf()
P.plot( x, rhoa0, x, rhoa1 )
P.legend( ('Node','CEM'), loc='best' )
P.grid()
P.xlabel( 'pole-dipole separation [m]' )
P.ylabel( r'$\rho_a$ in $\Omega$m' )
P.show()