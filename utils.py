import folium
from folium import DivIcon
from folium.plugins import MeasureControl
from networkx import shortest_path
import networkx as nx
import numpy as np
from typing import List, Callable, Tuple
import itertools
from itertools import groupby
from matplotlib import colors
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import osmnx as ox
from osmnx import graph_from_place, config
from osmnx import graph_from_place, get_nearest_node, plot_graph_route
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim 


def calculate_distance_matrix_original(graph, coordinates):
    n = len(coordinates)
    distances_matrix = np.empty((n, n))

    for i in range(n):
        for j in range(n):
            source_node = ox.nearest_nodes(graph, *tuple(reversed(coordinates[i])))
            target_node = ox.nearest_nodes(graph, *tuple(reversed(coordinates[j])))
            start_time = time.time()
            distance = nx.shortest_path_length(G=graph,
                                                     source=source_node,
                                                     target=target_node,
                                                     weight='length')
            end_time = time.time()
            duration_ms = 1000*(end_time - start_time)
            print(f"shortest path took {duration_ms:0.0f} ms")
            distances_matrix[i][j] = distance / 1000

    return distances_matrix

def calculate_distance_matrix(graph, coordinates):
    n = len(coordinates)
    distances_matrix = np.empty((n, n))

    source_node = []
    target_node = []
    for i in range(n):
        for j in range(n):
            source_node.append(tuple(reversed(coordinates[i])))
            target_node.append(tuple(reversed(coordinates[j])))

    x1,y1 = zip(*source_node)
    x2,y2 = zip(*target_node)

    source_node = ox.nearest_nodes(graph,x1,y1)
    target_node = ox.nearest_nodes(graph,x2,y2)

    routes = ox.shortest_path(graph, source_node, target_node, weight="length", cpus=1)

    routes_lengths = []
    for route in routes:
        routes_lengths.append(int(sum(ox.utils_graph.get_route_edge_attributes(graph, route, "length"))))

    distances_matrix = np.array(routes_lengths).reshape(n,n)/1000

    return distances_matrix


def create_map(graph, path, route, hill_names, coordinates, distances,pontos):
    route_map = ox.plot_route_folium(graph, path,
                                        tiles="OpenStreetMap",
                                        tooltip=f"Total distance {np.sum(distances):0.2f} km")
    
    
    if coordinates[0] != coordinates[-1]:
        distances_final = np.append(distances, 0)
    else:
        distances_final = distances
    
    
    for i in range(len(route)):
        index = route[i]
        folium.Marker(coordinates[index],
                      tooltip=f'''{i}: {hill_names[index]}; {distances_final[i]:0.2f} km to next hill''').add_to(route_map)
        folium.map.Marker(
            coordinates[index],
            icon=DivIcon(
                icon_size=(250, 36),
                icon_anchor=(0, 0),
                html='<div style="font-size: 15pt">' + str(i) + '</div>',
            )
        ).add_to(route_map)
    
    
    



    return route_map

def calculate_full_path(graph, route, coordinates):
    orig = []
    dest = []
    for i in range(0, len(route)-1):
        orig.append(tuple(reversed(coordinates[route[i]])))
        dest.append(tuple(reversed(coordinates[route[i+1]])))

    x1,y1 = zip(*orig)
    x2,y2 = zip(*dest)

    source_node = ox.nearest_nodes(graph,x1,y1)
    target_node = ox.nearest_nodes(graph,x2,y2)

    routes = ox.shortest_path(graph, source_node, target_node, weight="length", cpus=1)
    
    merged = list(itertools.chain(*routes))

    # for item in routes:
    #     if len(item) != 1:
    #         item.pop()
    #     else:
    #         routes.remove(item)

    routes_lengths = []
    for route in routes:
        routes_lengths.append(int(sum(ox.utils_graph.get_route_edge_attributes(graph, route, "length"))))
    
    distances = np.array(routes_lengths)/1000
    
    # remove [2,3, 3, 3, 5, 6, 6] -> [2,3,5,6]
    merged = [key for key, _group in groupby(merged)]

    
    return merged, distances

# https://omyllymaki.medium.com/conquering-seven-hills-route-optimization-with-sa-d96ace682e2c
def calculate_full_path_original(graph, route, coordinates):
    full_path = []
    distances = []
    for i in range(0, len(route) - 1):
        from_index = route[i]
        end_index = route[i + 1]

        source_node = ox.nearest_nodes(graph, *tuple(reversed(coordinates[from_index])))
        target_node = ox.nearest_nodes(graph, *tuple(reversed(coordinates[end_index])))

        path = nx.shortest_path(graph, source_node, target_node, weight='length')

        distance = nx.shortest_path_length(G=graph, source=source_node, target=target_node,
                                                 weight='length') / 1000
        distances.append(distance)

        full_path += path[1:]

    return full_path, distances


def create_init_route(start, end, n):
    route = [k for k in range(n)]
    if start in route:
        route.remove(start)
    if end in route:
        route.remove(end)
    route = [start] + route + [end]
    return route

def generate_graph(city, state):
    place = [{"city": city, "State": state, "country": 'Brazil'}]
    graph = graph_from_place(place, network_type='drive')
    return graph

def get_location(pontos, city, state):
    HILLS = {}
    pontos = pontos.split(',')
    points = tuple(pontos)
    lugar = Nominatim(user_agent="GetLoc")
    for i in range(0, len(points)):
        loc = lugar.geocode(points[i] + " " + city + " " + state)
        HILLS[str(i)] = loc[-1]
    START_HILL = "0"
    END_HILL =  str(len(points)-1)
    return HILLS, START_HILL, END_HILL