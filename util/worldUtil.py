#!/usr/bin/env python

import math

import numpy as np
import pygimli.meshtools as mt

def generate_hom_world_with_inclusion(world_dim: list, incl_start: list, incl_dim: list):
    """ Creates a homogeneous world with inclusion.

    Utility function to create a homogeneous world with an inclusion. Region markers are set to 1 for the background
    world and 2 for the inclusion.

    Parameter:
        world_dim: World dimensions as [x,z].
        incl_start: Inclusion upper left corner as [x,z].
        incl_dim: Inclusion dimension as [x,z].

    Returns:
        The created world.
    """
    # Create geometric objects
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])
    inclusion = mt.createRectangle(start=incl_start, end=[incl_start[0]+incl_dim[0], incl_start[1]-incl_dim[1]],
                                   marker=2, boundaryMarker=10)
    # Merge geometries
    geom = mt.mergePLC([world, inclusion])
    return geom

def generate_layered_world(world_dim: list, layer_heights: list):
    """ Creates a layered world.

    Utility function to create a layered world. Region markers are starting at 1 and increasing with depth.

    Parameter:
        world_dim: World dimensions as [x,z].
        layer_heights: Heights of the single layers.

    Returns:
        The created world.
    """
    # Check parameter integrity
    if sum(layer_heights) > world_dim[1]:
        return None
    # Create geometric objects
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])
    current_depth = 0
    layers = []
    for i in range(len(layer_heights)):
        layer = mt.createRectangle(start=[0, -current_depth], end=[world_dim[0], -(current_depth + layer_heights[i])],
                                   marker=i + 1, boundaryMarker=10)
        current_depth += layer_heights[i]
        layers.append(layer)
    if current_depth != world_dim[1]:
        layer = mt.createRectangle(start=[0, -current_depth], end=[world_dim[0], -world_dim[1]],
                                   marker=i + 2, boundaryMarker=10)
        layers.append(layer)
    # Merge geometries
    geom = mt.mergePLC([world] + layers)
    return geom

def generate_layered_world_with_inclusion(world_dim: list, layer_heights: list, incl_start: list, incl_dim: list):
    """ Creates a layered world with inclusion.

    Utility function to create a layered world with an inclusion. Region markers are starting at 1 and increasing with
    depth. The inclusion has the highest marker number.

    Parameter:
        world_dim: World dimensions as [x,z].
        layer_heights: Heights of the single layers.
        incl_start: Inclusion upper left corner as [x,z].
        incl_dim: Inclusion dimension as [x,z].

    Returns:
        The created world.
    """
    # Check parameter integrity
    if sum(layer_heights) > world_dim[1]:
        return None
    # Create geometric objects
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])
    current_depth = 0
    layers = []
    for i in range(len(layer_heights)):
        layer = mt.createRectangle(start=[0, -current_depth], end=[world_dim[0], -(current_depth + layer_heights[i])],
                                   marker=i + 1, boundaryMarker=10)
        current_depth += layer_heights[i]
        layers.append(layer)
    if current_depth != world_dim[1]:
        layer = mt.createRectangle(start=[0, -current_depth], end=[world_dim[0], -world_dim[1]],
                                   marker=i + 2, boundaryMarker=10)
        layers.append(layer)
    inclusion = mt.createRectangle(start=incl_start, end=[incl_start[0] + incl_dim[0], incl_start[1] - incl_dim[1]],
                                   marker=len(layers) + 1, boundaryMarker=10)
    # Merge geometries
    geom = mt.mergePLC([world, inclusion] + layers)
    return geom

def generate_dipped_layered_world(world_dim: list, layer_borders: list, dipping_angle: float):
    """ Creates a dipped layered world.

    Utility function to create a dipped layered world. Region markers are increasing with depth.

    Parameter:
        world_dim: World dimensions as [x,z].
        layer_borders: List of layer borders at world X = 0.
        dipping_angle: Angle at which the layers are dipping. Value describing counter-clockwise angle.

    Returns:
        The created world.
    """
    # Nested function to find the index to add a specific node
    def get_insert_index(nodes, node):
        i = 0
        # Get edge starting index
        while (i < len(nodes)) and (nodes[i][3] < node[3]):
            i = i + 1
        edge_start = i
        # Get edge ending index
        while (i < len(nodes)) and (nodes[i][3] <= node[3]):
            i = i + 1
        edge_end = i
        # Check for input error
        if (node[3] == 0) or (node[3] == 2) or (node[3] == 4) or (node[3] == 6):
            print('Function can only be used for non-default edges (1,3,5,7)')
            return -1
        # Find index based on specific edge
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
    # Nested function to find the connecting node of a given node
    def get_connecting_node(nodes_list, node, node_connections_list):
        for i in range(len(node_connections_list)):
            if node_connections_list[i][0] == nodes_list[node][0]:
                for j in range(len(nodes_list)):
                    if node_connections_list[i][1] == nodes_list[j][0]:
                        return j
        return -1
    # Nested function to find the next node on the world border
    def get_next_node(nodes_list, current_node):
        if current_node >= len(nodes_list) - 1:
            return 0
        else:
            return current_node + 1
    # Nested function to create a polygon from a set of nodes
    def get_polygon_from_nodes(node_set):
        vertices = []
        for i in range(len(node_set)):
            vertices.append([node_set[i][1], node_set[i][2]])
        return vertices
    # Correct angle
    while dipping_angle > 180:
        dipping_angle -= 360
    while dipping_angle < -180:
        dipping_angle += 360
    # Create background world
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]], worldMarker=True)
    # Remove layers out of world scope
    removed_indices = 0
    for i in range(len(layer_borders)):
        if (dipping_angle >= 0 and layer_borders[i - removed_indices] > 0) or (
                dipping_angle <= 0 and layer_borders[i - removed_indices] < -world_dim[1]):
            layer_borders.pop(i - removed_indices)
            removed_indices = removed_indices + 1
    # Compute layer height difference based on dipping angle
    dipping_diff = world_dim[0] * math.tan(dipping_angle / 180 * math.pi)
    # Compute nodes on world border (id,x,y,edge)
    nodes = [[0, 0, 0, 0], [1, world_dim[0], 0, 2], [2, world_dim[0], -world_dim[1], 4], [3, 0, -world_dim[1], 6]]
    node_connections = []
    next_id = 4
    for i in range(len(layer_borders)):
        # Find starting node
        if layer_borders[i] <= 0 and layer_borders[i] >= -world_dim[1]:
            # Layer starts at left world border (default case)
            start_node = [next_id, 0, layer_borders[i], 7]
        else:
            if layer_borders[i] > 0:
                # Layer starts above world
                x = layer_borders[i] * math.tan((90 + dipping_angle) * math.pi / 180)
                start_node = [next_id, x, 0, 1]
            else:
                # Layer starts below world
                x = -(layer_borders[i] + world_dim[1]) * math.tan((90 - dipping_angle) * math.pi / 180)
                start_node = [next_id, x, -world_dim[1], 5]
        nodes.insert(get_insert_index(nodes, start_node), start_node)
        next_id = next_id + 1
        # Find ending node
        if layer_borders[i] + dipping_diff <= 0 and layer_borders[i] + dipping_diff >= -world_dim[1]:
            # Layer ends at right world border (default case)
            end_node = [next_id, world_dim[0], layer_borders[i] + dipping_diff, 3]
        else:
            if layer_borders[i] + dipping_diff > 0:
                # Layer ends above world
                x = -layer_borders[i] / math.tan(dipping_angle / 180 * math.pi)
                end_node = [next_id, x, 0, 1]
            else:
                # Layer ends below world
                x = world_dim[0] - (layer_borders[i] + dipping_diff + world_dim[1]) / math.tan(
                    dipping_angle / 180 * math.pi)
                end_node = [next_id, x, -world_dim[1], 5]
        nodes.insert(get_insert_index(nodes, end_node), end_node)
        next_id = next_id + 1
        # Save node connections
        node_connections.append([start_node[0], end_node[0]])
        node_connections.append([end_node[0], start_node[0]])
    # Compute polygons from nodes
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
    # Merge geometries
    for i in range(len(polygons)):
        poly = mt.createPolygon(get_polygon_from_nodes(polygons[i]), marker=i + 1, isClosed=True)
        world = mt.mergePLC([world, poly])
    return world

def generate_tiled_world(world_dim: list, tile_size: list):
    """ Creates a tiled layered world.

        Utility function to create a tiled layered world. Region marker 1 is upper left corner.

        Parameter:
            world_dim: World dimensions as [x,z].
            tile_size: Tile dimensions as [x,z].

        Returns:
            The created world.
        """
    # Create world
    world = mt.createWorld(start=[0, 0], end=[world_dim[0], -world_dim[1]])
    # Create tile counts
    n_tiles_x = int(np.ceil(world_dim[0] / tile_size[0]))
    n_tiles_y = int(np.ceil(world_dim[1] / tile_size[1]))
    # Create and merge tiles
    for j in range(n_tiles_y):
        for i in range(n_tiles_x):
            x_start = int(i * tile_size[0])
            x_end = int((i + 1) * tile_size[0])
            y_start = int(-j * tile_size[1])
            y_end = int(-(j + 1) * tile_size[1])
            if x_end > world_dim[0]:
                x_end = world_dim[0]
            if y_end < -world_dim[1]:
                y_end = -world_dim[1]
            marker = 1
            if ((-1) ** i) * ((-1) ** j) < 0:
                marker = 2
            tile = mt.createRectangle(start=[x_start, y_start], end=[x_end, y_end], marker=marker, boundaryMarker=10)
            world = mt.mergePLC([world, tile])
    return world
