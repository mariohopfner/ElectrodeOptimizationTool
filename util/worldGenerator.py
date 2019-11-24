#!/usr/bin/env python

import math
import pygimli.meshtools as mt

def get_insert_index(nodes, node):
    i = 0
    # get edge start index
    while (i < len(nodes)) and (nodes[i][3] < node[3]):
        i = i + 1
    edge_start = i

    # get edge end index
    while (i < len(nodes)) and (nodes[i][3] <= node[3]):
        i = i + 1
    edge_end = i

    if (node[3] == 0) or (node[3] == 2) or (node[3] == 4) or (node[3] == 6):
        print("Function can only be used for non-default edges (1,3,5,7)")
        return -1

    i = edge_start
    if node[3] == 1:
        while (i < edge_end) and (node[1] > nodes[i][1]):
            i = i + 1

    if node[3] == 3:
        while (i < edge_end) and (node[2] < nodes[i][2]):
            i = i + 1

    if node[3] == 5:
        while (i < edge_end) and (node[1] < nodes[i][1]):
            i = i + 1

    if node[3] == 7:
        while (i < edge_end) and (node[2] > nodes[i][2]):
            i = i + 1

    return i


def get_connecting_node(nodes, node, node_connections):
    for i in range(len(node_connections)):
        if node_connections[i][0] == nodes[node][0]:
            for j in range(len(nodes)):
                if node_connections[i][1] == nodes[j][0]:
                    return j
    return -1


def get_next_node(nodes, current_node):
    if current_node >= len(nodes) - 1:
        return 0
    else:
        return current_node + 1


def get_polygon_from_nodes(node_set):
    vertices = []
    for i in range(len(node_set)):
        vertices.append([node_set[i][1], node_set[i][2]])
    return vertices

'''
Generates a homogeneous world with a single inclusion.
The region markers are 1 for the world and 2 for the inclusion.
    :parameter
        world_dim_x        - world dimensions as [x,y]
        incl_start_x       - upper left corner of the inclusion as [x,y]
        incl_dim_x         - inclusion dimensions as [x,y]
'''
def generate_hom_world_with_inclusion(world_dim=[100, 100], incl_start=[10, -10], incl_dim=[10, 10]):
    # create world
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])

    # create inclusion
    inclusion = mt.createRectangle(start=incl_start, end=[incl_start[0]+incl_dim[0], incl_start[1]-incl_dim[1]],
                                   marker=2, boundaryMarker=10)

    # merge underground
    geom = mt.mergePLC([world, inclusion])

    return geom

'''
Generates a layered world with a single inclusion.
The region markers are increasing with depth, the inclusion has the next available marker number
    :parameter
        world_dim_x        - world dimensions as [x,y]
        layer_heights      - heights of the layers (at least one height needs to be given)
        incl_start_x       - upper left corner of the inclusion as [x,y]
        incl_dim_x         - inclusion dimensions as [x,y]
'''
def generate_layered_world_with_inclusion(world_dim=[100, 100], layer_heights=[10, 20], incl_start=[10, -10],
                                          incl_dim=[10, 10]):
    # pre-computational checks
    if sum(layer_heights) > world_dim[1]:
        return None

    # create world
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])

    # create layers
    current_depth = 0
    layers = []
    for i in range(len(layer_heights)):
        layer = mt.createRectangle(start=[0, -current_depth], end=[world_dim[0], -(current_depth + layer_heights[i])],
                                   marker=i + 1, boundaryMarker=10)
        current_depth += layer_heights[i]
        layers.append(layer)

    # add bottom layer if needed
    if current_depth != world_dim[1]:
        layer = mt.createRectangle(start=[0, -current_depth], end=[world_dim[0], -world_dim[1]],
                                   marker=i + 2, boundaryMarker=10)
        layers.append(layer)

    # create inclusion
    inclusion = mt.createRectangle(start=incl_start, end=[incl_start[0] + incl_dim[0], incl_start[1] - incl_dim[1]],
                                   marker=len(layers) + 1, boundaryMarker=10)

    # merge underground
    geom = mt.mergePLC([world, inclusion] + layers)

    return geom

'''
Generates a dipped layered world.
    :parameter
        world_dim_x        - world dimensions as [x,y]
        layer_heights      - heights of the layers (at least one height needs to be given)
        dipping_angle      - angle at which the layers are dipping
'''
def generate_dipped_layered_world(world_dim=[100, 100], layer_ends=[-20, -50], dipping_angle=30):
    # pre-correct angle
    while dipping_angle > 180:
        dipping_angle -= 360

    while dipping_angle < -180:
        dipping_angle += 360

    # create world
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])

    # remove layers out of world scope
    removed_indices = 0
    for i in range(len(layer_ends)):
        if (dipping_angle >= 0 and layer_ends[i - removed_indices] > 0) or (
                dipping_angle <= 0 and layer_ends[i - removed_indices] < -world_dim[1]):
            layer_ends.pop(i - removed_indices)
            removed_indices = removed_indices + 1

    # compute layer height difference based on dipping angle
    dipping_diff = world_dim[0] * math.tan(dipping_angle / 180 * math.pi)

    # compute nodes (id,x,y,edge)
    nodes = [[0, 0, 0, 0], [1, world_dim[0], 0, 2], [2, world_dim[0], -world_dim[1], 4], [3, 0, -world_dim[1], 6]]
    node_connections = []
    next_id = 4
    for i in range(len(layer_ends)):
        # starting node
        start_node = [0, 0, 0, 0]
        if layer_ends[i] <= 0 and layer_ends[i] >= -world_dim[1]:
            # layer starts at left world border
            start_node = [next_id, 0, layer_ends[i], 7]
        else:
            if layer_ends[i] > 0:
                # layer starts above world
                x = layer_ends[i] * math.tan((90 + dipping_angle) * math.pi / 180)
                start_node = [next_id, x, 0, 1]
            else:
                # layer starts below world
                x = -(layer_ends[i] + world_dim[1]) * math.tan((90 - dipping_angle) * math.pi / 180)
                start_node = [next_id, x, -world_dim[1], 5]
        nodes.insert(get_insert_index(nodes, start_node), start_node)
        next_id = next_id + 1
        # ending node
        end_node = [0, 0, 0, 0]
        if layer_ends[i] + dipping_diff <= 0 and layer_ends[i] + dipping_diff >= -world_dim[1]:
            # layer ends at right world border
            end_node = [next_id, world_dim[0], layer_ends[i] + dipping_diff, 3]
        else:
            if layer_ends[i] + dipping_diff > 0:
                # layer ends above world
                x = -layer_ends[i] / math.tan(dipping_angle / 180 * math.pi)
                end_node = [next_id, x, 0, 1]
            else:
                # layer ends below world
                x = world_dim[0] - (layer_ends[i] + dipping_diff + world_dim[1]) / math.tan(
                    dipping_angle / 180 * math.pi)
                end_node = [next_id, x, -world_dim[1], 5]
        nodes.insert(get_insert_index(nodes, end_node), end_node)
        next_id = next_id + 1
        # save node connections
        node_connections.append([start_node[0], end_node[0]])
        node_connections.append([end_node[0], start_node[0]])

    # compute polygons
    polygons = []
    first_node = 0
    edge_to_finish = 4
    if dipping_angle < 0:
        for i in range(len(nodes)):
            if nodes[i][3] == 2:
                break
        first_node = i
        edge_to_finish = 6

    while edge_to_finish != -1:
        polygon = []
        last_node_was_connected = False
        has_connected_nodes = False
        current_node_index = first_node
        polygon.append(nodes[first_node])
        while (len(polygon) == 1) or (polygon[len(polygon) - 1] != polygon[0]):
            if (last_node_was_connected == False) and (len(polygon) != 1) and (
                    get_connecting_node(nodes, current_node_index, node_connections) != -1):
                current_node_index = get_connecting_node(nodes, current_node_index, node_connections)
                polygon.append(nodes[current_node_index])
                last_node_was_connected = True
                has_connected_nodes = True
                if nodes[current_node_index][3] == edge_to_finish:
                    edge_to_finish = -1
                continue
            current_node_index = get_next_node(nodes, current_node_index)
            polygon.append(nodes[current_node_index])
            if not has_connected_nodes:
                first_node = current_node_index
            last_node_was_connected = False
            if nodes[current_node_index][3] == edge_to_finish:
                edge_to_finish = -1
        polygons.append(polygon[:-1])

    # merge underground
    for i in range(len(polygons)):
        poly = mt.createPolygon(get_polygon_from_nodes(polygons[i]), marker=i + 1, isClosed=True)
        world = mt.mergePLC([world, poly])
    return world









'''
Function that creates a PyGimli world with given parameters
    :parameter
        scheme_file        - name of the scheme file
        x                  - length of world in x dimension
        y                  - length of world in y dimension
        layers             - depths of subsurface-splitting horizons
'''
# def generate_simple_layered_world(scheme_file, x=100, y=100, layers=None):
#     if layers is None:
#         layers = []
#
#     # if first layer is the surface layer, remove it
#     if len(layers) > 0 and layers[0] == 0:
#         layers.pop(0)
#
#     # create world
#     world = mt.createWorld(start=[0,0], end=[x,-y], layers=layers)
#
#     # load given scheme file
#     scheme = pb.load(scheme_file)
#
#     # add electrodes defined in scheme file
#     for s in scheme.sensors():
#         world.createNode(s + [0.0, -0.2])
#
#     return world
