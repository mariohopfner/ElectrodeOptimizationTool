#!/usr/bin/env python

import os
import logging

import pybert as pb

def merge_schemes(scheme1: pb.DataContainerERT, scheme2: pb.DataContainerERT, tmp_dir: str, remove_tmp_file=True):
    """ Merges to schemes while prioritizing the first one.

    Utility function to merge to schemes. Electrode positions can differ. Electrodes on same positions will be merged.
    When multiple measurements are available for the same electrode configuration, the data from scheme1 will be used.

    Parameter:
        scheme1: First scheme to be merged. This scheme will be prioritized.
        scheme2: Second scheme to be merged.
        tmp_dir: Directory to temporarily store files in.
        remove_tmp_file: (optional) Whether the temporary file(s) should be removed when no longer necessary. Should
                         only be disabled for debugging purposes.

    Returns:
        The merged scheme.
    """
    logging.info('Merging datasets with %d and %d entries', len(scheme1('rhoa')), len(scheme2('rhoa')))
    # Create global electrode register
    electrodes = []
    scheme1_electrodes = scheme1.sensorPositions()
    for i in range(len(scheme1_electrodes)):
        electrodes.append(scheme1_electrodes[i])
    scheme2_electrodes = scheme2.sensorPositions()
    for i in range(len(scheme2_electrodes)):
        if scheme2_electrodes[i] not in electrodes:
            electrodes.append(scheme2_electrodes[i])
    # Create electrode dictionaries
    scheme1_dic = {-1: -1}
    for i in range(len(scheme1_electrodes)):
        scheme1_dic.update({i: i})
    scheme2_dic = {-1: -1}
    for i in range(len(scheme2_electrodes)):
        for j in range(len(electrodes)):
            if scheme2_electrodes[i] == electrodes[j]:
                scheme2_dic.update({i: j})
    # Merge data
    # (sensors: a b m n)
    # (data: err i ip iperr k r rhoa u valid)
    scheme_sensors = []
    scheme_data = []
    for i in range(len(scheme1('rhoa'))):
        scheme_sensors.append([
            scheme1_dic[scheme1('a')[i]]+1,
            scheme1_dic[scheme1('b')[i]]+1,
            scheme1_dic[scheme1('m')[i]]+1,
            scheme1_dic[scheme1('n')[i]]+1
        ])
        scheme_data.append([
            scheme1('err')[i],
            scheme1('i')[i],
            scheme1('ip')[i],
            scheme1('iperr')[i],
            scheme1('k')[i],
            scheme1('r')[i],
            scheme1('rhoa')[i],
            scheme1('u')[i],
            scheme1('valid')[i],
        ])

    for i in range(len(scheme2('rhoa'))):
        a = scheme2_dic[scheme2('a')[i]]+1
        b = scheme2_dic[scheme2('b')[i]]+1
        m = scheme2_dic[scheme2('m')[i]]+1
        n = scheme2_dic[scheme2('n')[i]]+1
        if [a, b, m, n] not in scheme_sensors:
            scheme_sensors.append([
                a,
                b,
                m,
                n
            ])
            scheme_data.append([
                scheme2('err')[i],
                scheme2('i')[i],
                scheme2('ip')[i],
                scheme2('iperr')[i],
                scheme2('k')[i],
                scheme2('r')[i],
                scheme2('rhoa')[i],
                scheme2('u')[i],
                scheme2('valid')[i],
            ])
    logging.info('Merging complete (%d entries)', len(scheme_data))

    # Write to temporary file
    tmp_file = tmp_dir + 'tmpMerge.shm'
    f = open(tmp_file, 'w')
    # - electrodes
    f.write('%d\n' % len(electrodes))
    f.write('# x y z\n')
    for i in range(len(electrodes)):
        f.write('%f %f %f\n' % (electrodes[i][0],electrodes[i][1],electrodes[i][2]))
    # - data
    f.write('%d\n' % len(scheme_data))
    f.write('# a b m n err i ip iperr k r rhoa u valid \n')
    for i in range(len(scheme_data)):
        f.write('%d %d %d %d %f %f %f %f %f %f %f %f %d\n' % (
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
    f.write('0\n')
    f.close()
    # Read file again to not generate any inconsistencies
    result = pb.load(tmp_file)
    if remove_tmp_file:
        os.remove(tmp_file)
    return result

def find_duplicate_configurations(scheme1: pb.DataContainerERT, scheme2: pb.DataContainerERT):
    """ Finds configurations of scheme1 which are also defined in scheme2.

    Utility function to find duplicates electrode configurations contained in both schemes.

    Parameter:
        scheme1: The first scheme to be checked for duplicates.
        scheme2: The second scheme to be checked for duplicates.

    Returns:
        The duplicate indices of scheme1.
    """
    logging.info('Finding duplicate configurations for datasets with %d and %d entries',
                 len(scheme1('rhoa')), len(scheme2('rhoa')))
    # Create global electrode register
    electrodes = []
    scheme1_electrodes = scheme1.sensorPositions()
    for i in range(len(scheme1_electrodes)):
        electrodes.append(scheme1_electrodes[i])
    scheme2_electrodes = scheme2.sensorPositions()
    # Create electrode dictionaries
    scheme1_dic = {-1: -1}
    for i in range(len(scheme1_electrodes)):
        scheme1_dic.update({i: i})
    scheme2_dic = {-1: -1}
    for i in range(len(scheme2_electrodes)):
        for j in range(len(electrodes)):
            if scheme2_electrodes[i] == electrodes[j]:
                scheme2_dic.update({i: j})
    # Subtract configurations
    scheme_sensors = []
    for i in range(len(scheme1('rhoa'))):
        scheme_sensors.append([
            scheme1_dic[scheme1('a')[i]],
            scheme1_dic[scheme1('b')[i]],
            scheme1_dic[scheme1('m')[i]],
            scheme1_dic[scheme1('n')[i]]
        ])
    indices = []
    for i in range(len(scheme2('rhoa'))):
        indices.append(scheme_sensors.index([
            scheme2_dic[scheme2('a')[i]],
            scheme2_dic[scheme2('b')[i]],
            scheme2_dic[scheme2('m')[i]],
            scheme2_dic[scheme2('n')[i]]
        ]))
    logging.info('Finding duplicates complete (%d entries)', len(indices))
    return indices

def extract_configs_from_scheme(scheme: pb.DataContainerERT, config_indices: list, tmp_dir: str, remove_tmp_file=True):
    """ Extract specific electrode configurations from scheme.

    Utility function to extract specific electrode configurations (identified by index) from a given scheme. Extracted
    data will be returned in a separate scheme.

    Parameter:
        scheme: The scheme the electrode configurations should be extracted from.
        config_indices: The indices of the configurations to be extracted.
        tmp_dir: Directory to temporarily store files in.
        remove_tmp_file: (optional) Whether the temporary file(s) should be removed when no longer necessary. Should
                         only be disabled for debugging purposes.

    Returns:
        A scheme containing the extracted configurations.
    """
    logging.info('Extracting configs from scheme...')
    tmp_file = tmp_dir + 'tmpExtract.shm'
    f = open(tmp_file, 'w')
    # Write electrodes to file
    electrodes = scheme.sensorPositions()
    f.write('%d\n' % len(electrodes))
    f.write('# x y z\n')
    for i in range(len(electrodes)):
        f.write('%f %f %f\n' % (electrodes[i][0], electrodes[i][1], electrodes[i][2]))
    # Extract configurations and write to file
    f.write('%d\n' % len(config_indices))
    f.write('# a b m n err i ip iperr k r rhoa u valid \n')
    for i in config_indices:
        f.write('%d %d %d %d %f %f %f %f %f %f %f %f %d\n' % (
            scheme('a')[i]+1,
            scheme('b')[i]+1,
            scheme('m')[i]+1,
            scheme('n')[i]+1,
            scheme('err')[i],
            scheme('i')[i],
            scheme('ip')[i],
            scheme('iperr')[i],
            scheme('k')[i],
            scheme('r')[i],
            scheme('rhoa')[i],
            scheme('u')[i],
            scheme('valid')[i]
        ))
    f.write('0\n')
    f.close()
    # Read file again to not generate any inconsistencies
    result = pb.load(tmp_file)
    if remove_tmp_file:
        os.remove(tmp_file)
    return result