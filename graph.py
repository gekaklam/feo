#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
import sys
import argparse

import pprint
import datetime
import time

# simulation and reporting facilities
import tapesim.Simulation as Simulation
import tapesim.Topology as Topology
import tapesim.Report as Report

# import datatypes required used in this simulation
import tapesim.datatypes.Request as Request

# import hardware components required for this example
import tapesim.components.Client as Client
import tapesim.components.Switch as Switch
import tapesim.components.IOServer as IOServer
import tapesim.components.Drive as Drive
import tapesim.components.Library as Library

# import virtual components, usually schedulers and managers (e.g. lookup tables)
import tapesim.components.Cache as Cache
import tapesim.components.FileManager as FileManager
import tapesim.components.TapeManager as TapeManager



import graph_tool.all as gt
from numpy.random import poisson

###############################################################################
#
#g = gt.Graph(directed=False)
#
#v1 = g.add_vertex()
#v2 = g.add_vertex()
#e = g.add_edge(v1, v2)
#
#gt.graph_draw(g, output="manual.pdf")
#
#for v in g.vertices():
#    print(v)
#
#print("---")
###############################################################################

g = gt.load_graph("configs/network.xml")


edges = []
for e in g.edges():
    #edges.append((e.source(), e.target(), g.ep.weight[e]))
    edges.append(e)

for e in edges:
    new_edge = g.add_edge(e.target(), e.source(), add_missing=True)
    g.ep['weight'][new_edge] = g.ep['weight'][e]



s = Simulation.Simulation()

for v in g.vertices():
    print(v, g.vp.name[v], g.vp['eval'][v])
    print(g.vp['_graphml_vertex_id'][v])
    classname = g.vp.name[v].split(":")[0]

    #if g.vp['eval'][v]:
    #    obj = eval(g.vp['eval'][v])
    #    print("from eval:", obj)
    #else:
    #    obj = eval("%s.%s(s)" % (classname,classname))
    #    print("from name:", obj)

    
    print("\n")


name = g.vp["name"]
print(dir(name))
print(name.get_array)
weight = g.ep["weight"]

print()

# default graph

# prepare label text
edge_label = g.new_edge_property("string")
gt.map_property_values(weight, edge_label, lambda x: str(x))

pos = gt.sfdp_layout(g)
gt.graph_draw(g, pos=pos,
    vertex_text=name, 
    #vertex_fill_color=[1, 1, 1, 0.9],
    #vertex_color=[0.0, 0.0, 0.0, 1.0],
    edge_pen_width=gt.prop_to_size(weight, mi=1, ma=10, power=1),
    edge_text=edge_label,
    output="outputs/fromxml.pdf")

# different layout
#pos = gt.arf_layout(g, max_iter=0)
#pos = gt.radial_tree_layout(g, g.vertex(0))
#gt.graph_draw(g, pos=pos, vertex_text=name, edge_pen_width=weight, output="outputs/fromxml.pdf")

# not really useful
#state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True)
#gt.draw_hierarchy(state, vertex_text=name, output="outputs/fromxml.pdf")

# somewhat useful as it nicely resambles the flow?
#g = gt.GraphView(g, vfilt=gt.label_largest_component(g))
#g.purge_vertices()
#state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True)
#t = gt.get_hierarchy_tree(state)[0]
#tpos = pos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() - 1), weighted=True)
#cts = gt.get_hierarchy_control_points(g, t, tpos)
#pos_circle = g.own_property(tpos)
#b = state.levels[0].b
#shape = b.copy()
#shape.a %= 14
#
#gt.graph_draw(g, pos=pos, 
#        edge_color=[0, 0, 0, 0.3], 
#        edge_control_points=cts,
#        edge_pen_width=weight, 
#        vertex_anchor=0, 
#        vertex_fill_color=b, 
#        vertex_shape=shape, 
#        vertex_text=name, 
#        output="outputs/fromxml_hierarchical.pdf")
#

# available properties in graph
g.list_properties()
print()

# quick list for index to node
for v in g.vertices():
    print(v, g.vp.name[v], ",", g.vp['_graphml_vertex_id'][v])
print()

# shortest path
print("---")
print("Shortest-Path")
vlist, elist = gt.shortest_path(g, g.vertex(0), g.vertex(7))
print([str(v) for v in vlist])
print([str(e) for e in elist])

# max flow
print("---")
print("Max-Flow Min-Cut")
cap = g.edge_properties["weight"]
src, tgt = g.vertex(7), g.vertex(0)
res = gt.push_relabel_max_flow(g, src, tgt, cap)
#res = gt.boykov_kolmogorov_max_flow(g, src, tgt, cap)
res.a = cap.a - res.a
max_flow = sum(res[e] for e in tgt.in_edges())
print(max_flow)

# prepare label text
edge_label = g.new_edge_property("string")
gt.map_property_values(res, edge_label, lambda x: str(x))

gt.graph_draw(g, pos=pos,
    edge_pen_width=gt.prop_to_size(res, mi=1, ma=15, power=1),    
    vertex_text=name, 
    edge_text=edge_label, 
    output="outputs/max_flow.pdf")


print()

for e in g.edges():
    print(e, g.ep.weight[e], g.vp['name'][e.source()], " -> ", g.vp['name'][e.target()], res[e])


print("---")
################################################################################
#
#g = gt.random_graph(20, lambda: (poisson(4), poisson(4)))
#vlist, elist = gt.shortest_path(g, g.vertex(10), g.vertex(11))
#
#gt.graph_draw(g, output="path.pdf")
