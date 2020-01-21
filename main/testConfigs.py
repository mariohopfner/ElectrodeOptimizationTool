#!/usr/bin/env python

import pygimli as pg
import pybert as pb

import util.schemeUtil as su

electrode_distribution = pg.utils.grange(start=0, end=100, n=5)
electrode_distribution2 = pg.utils.grange(start=0, end=100, n=9)
scheme1 = pb.createData(elecs=electrode_distribution, schemeName='pd')
scheme1a = pb.createData(elecs=electrode_distribution2, schemeName='pd')
scheme2 = pb.createData(elecs=electrode_distribution, schemeName='wa')

scheme1.save('scheme1.shm')
scheme1a.save('scheme1a.shm')

#scheme_merge = su.merge_schemes(scheme1,scheme2,'./',False)
idx = su.find_duplicate_configurations(scheme1a,scheme1)
print("xd")