#!/usr/bin/env python
import pybert as pb
import os
import logging

def merge_schemes(scheme1, scheme2, tmp_dir, remove_tmp_file=True):
    logging.info("Merging datasets with %d and %d entries", len(scheme1("rhoa")), len(scheme2("rhoa")))
    # create global electrode register
    electrodes = []
    scheme1_electrodes = scheme1.sensorPositions()
    for i in range(len(scheme1_electrodes)):
        electrodes.append(scheme1_electrodes[i])
    scheme2_electrodes = scheme2.sensorPositions()
    for i in range(len(scheme2_electrodes)):
        if scheme2_electrodes[i] not in electrodes:
            electrodes.append(scheme2_electrodes[i])

    # create electrode dictionaries
    scheme1_dic = {-1: -1}
    for i in range(len(scheme1_electrodes)):
        scheme1_dic.update({i: i})
    scheme2_dic = {-1: -1}
    for i in range(len(scheme2_electrodes)):
        for j in range(len(electrodes)):
            if scheme2_electrodes[i] == electrodes[j]:
                scheme2_dic.update({i: j})

    # sensors: a b m n
    # data: err i ip iperr k r rhoa u valid
    scheme_sensors = []
    scheme_data = []
    for i in range(len(scheme1("rhoa"))):
        scheme_sensors.append([
            scheme1_dic[scheme1("a")[i]]+1,
            scheme1_dic[scheme1("b")[i]]+1,
            scheme1_dic[scheme1("m")[i]]+1,
            scheme1_dic[scheme1("n")[i]]+1
        ])
        scheme_data.append([
            scheme1("err")[i],
            scheme1("i")[i],
            scheme1("ip")[i],
            scheme1("iperr")[i],
            scheme1("k")[i],
            scheme1("r")[i],
            scheme1("rhoa")[i],
            scheme1("u")[i],
            scheme1("valid")[i],
        ])

    for i in range(len(scheme2("rhoa"))):
        a = scheme2_dic[scheme2("a")[i]]+1
        b = scheme2_dic[scheme2("b")[i]]+1
        m = scheme2_dic[scheme2("m")[i]]+1
        n = scheme2_dic[scheme2("n")[i]]+1
        if [a, b, m, n] not in scheme_sensors:
            scheme_sensors.append([
                a,
                b,
                m,
                n
            ])
            scheme_data.append([
                scheme2("err")[i],
                scheme2("i")[i],
                scheme2("ip")[i],
                scheme2("iperr")[i],
                scheme2("k")[i],
                scheme2("r")[i],
                scheme2("rhoa")[i],
                scheme2("u")[i],
                scheme2("valid")[i],
            ])
    logging.info("Merging complete (%d entries)", len(scheme_data))

    # write to file
    tmp_file = tmp_dir + "tmpMerge.shm"
    f = open(tmp_file, "w")
    # - electrodes
    f.write("%d\n" % len(electrodes))
    f.write("# x y z\n")
    for i in range(len(electrodes)):
        f.write("%f %f %f\n" % (electrodes[i][0],electrodes[i][1],electrodes[i][2]))
    # - data
    f.write("%d\n" % len(scheme_data))
    f.write("# a b m n err i ip iperr k r rhoa u valid \n")
    for i in range(len(scheme_data)):
        f.write("%d %d %d %d %f %f %f %f %f %f %f %f %d\n" % (
            scheme_sensors[i][0],
            scheme_sensors[i][1],
            scheme_sensors[i][2],
            scheme_sensors[i][3],
            scheme_data[i][0],
            scheme_data[i][1],
            scheme_data[i][2],
            scheme_data[i][3],
            scheme_data[i][4],
            scheme_data[i][5],
            scheme_data[i][6],
            scheme_data[i][7],
            scheme_data[i][8]
        ))
    f.write("0\n")
    f.close()

    result = pb.load(tmp_file)

    if remove_tmp_file:
        os.remove(tmp_file)

    return result

def find_duplicate_configurations(scheme1, scheme2):
    logging.info("Finding duplicate configurations for datasets with %d and %d entries",
                 len(scheme1("rhoa")), len(scheme2("rhoa")))
    # create global electrode register
    electrodes = []
    scheme1_electrodes = scheme1.sensorPositions()
    for i in range(len(scheme1_electrodes)):
        electrodes.append(scheme1_electrodes[i])
    scheme2_electrodes = scheme2.sensorPositions()

    # create electrode dictionaries
    scheme1_dic = {-1: -1}
    for i in range(len(scheme1_electrodes)):
        scheme1_dic.update({i: i})
    scheme2_dic = {-1: -1}
    for i in range(len(scheme2_electrodes)):
        for j in range(len(electrodes)):
            if scheme2_electrodes[i] == electrodes[j]:
                scheme2_dic.update({i: j})

    # subtract configurations
    scheme_sensors = []
    for i in range(len(scheme1("rhoa"))):
        scheme_sensors.append([
            scheme1_dic[scheme1("a")[i]],
            scheme1_dic[scheme1("b")[i]],
            scheme1_dic[scheme1("m")[i]],
            scheme1_dic[scheme1("n")[i]]
        ])
    indices = []
    for i in range(len(scheme2("rhoa"))):
        indices.append(scheme_sensors.index([
            scheme2_dic[scheme2("a")[i]],
            scheme2_dic[scheme2("b")[i]],
            scheme2_dic[scheme2("m")[i]],
            scheme2_dic[scheme2("n")[i]]
        ]))
    logging.info("Finding duplicates complete (%d entries)", len(indices))
    return indices

def extract_configs_from_scheme(scheme, config_indices, tmp_dir, remove_tmp_file=True):
    # write to file
    logging.info("Extracting configs from scheme...")
    tmp_file = tmp_dir + "tmpExtract.shm"
    f = open(tmp_file, "w")
    # - electrodes
    electrodes = scheme.sensorPositions()
    f.write("%d\n" % len(electrodes))
    f.write("# x y z\n")
    for i in range(len(electrodes)):
        f.write("%f %f %f\n" % (electrodes[i][0], electrodes[i][1], electrodes[i][2]))
    # - data
    f.write("%d\n" % len(config_indices))
    f.write("# a b m n err i ip iperr k r rhoa u valid \n")
    for i in config_indices:
        f.write("%d %d %d %d %f %f %f %f %f %f %f %f %d\n" % (
            scheme("a")[i]+1,
            scheme("b")[i]+1,
            scheme("m")[i]+1,
            scheme("n")[i]+1,
            scheme("err")[i],
            scheme("i")[i],
            scheme("ip")[i],
            scheme("iperr")[i],
            scheme("k")[i],
            scheme("r")[i],
            scheme("rhoa")[i],
            scheme("u")[i],
            scheme("valid")[i]
        ))
    f.write("0\n")
    f.close()

    result = pb.load(tmp_file)

    if remove_tmp_file:
        os.remove(tmp_file)

    return result