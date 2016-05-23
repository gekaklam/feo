#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2015 Jakob Luettgau
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import graph_tool.all as gt
import cairo

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


class Topology(object):

    def __init__(self, simulation, network_xml=None, tape_xml=None):

        self.simulation = simulation
        self.network = None
        self.tape = None

        self.components = []
        self.clients = []
        self.servers = []
        self.drives = []

        self.nodeswitch = None
        self.driveswitch = None

        if network_xml:
            self.network_from_xml(network_xml)

        if tape_xml:
            self.tape_from_xml(tape_xml)

        pass


    def get_path(self, src, tgt):
        g = self.graph
        vlist, elist = gt.shortest_path(g, g.vertex(src), g.vertex(tgt))
        return vlist, elist


    def dump_vertex_property(self, prop):
        g = self.graph
        for v in g.vertices():
            print(v, ":", prop[v])

    def dump_edge_property(self, prop):
        g = self.graph
        for e in g.edges():
            print(e, ":", prop[e])


    def max_flow(self, src, tgt):
        g = self.graph
        pos = self.pos

        cap = g.ep['capacity']
        #self.dump_edge_property(cap)
        #self.draw_graph(cap, 'visualisation/current-capacity.pdf')

        src, tgt = g.vertex(src), g.vertex(tgt)
        res = gt.push_relabel_max_flow(g, src, tgt, cap)
        #res = gt.boykov_kolmogorov_max_flow(g, src, tgt, cap)

        res.a = cap.a - res.a
        max_flow = sum(res[e] for e in tgt.in_edges())

        #self.draw_graph(res, 'visualisation/current-max-flow.pdf')
        return res, max_flow

    def allocate_capacity(self, res):
        print("ALLOC TOPO")
        g = self.graph
        for e in g.edges():
            g.ep['capacity'][e] -= res[e]

    def free_capacity(self, res):
        print("FREE TOPO")
        g = self.graph
        for e in g.edges():
            g.ep['capacity'][e] += res[e]


    def register_network_component(self, name="NetworkComponent", attach_to=None, link_capacity=10, drive=False):
        s = self.simulation
        g = self.graph

        print("INFO: New network component added:", name)

        # register vertex, add properties
        v = g.add_vertex()
        #g.vp['name'][v] = name
        g.vp['name'][v] = name
        
        # create a new client 
       
        if drive:
            new_comp = Drive.Drive(s)
        else:
            new_comp = Client.Client(s)
        

        new_comp.nodeidx = int(v)
        new_comp.graph = g

        g.vp['obj'][v] = new_comp


        # if drive and 
        if drive and self.driveswitch != None and attach_to == None:
            attach_to = self.driveswitch

        # attach to, default behaivor
        if self.nodeswitch != None and attach_to == None:
            attach_to = self.nodeswitch

        if attach_to != None:
            # make full duplex
            e1 = g.add_edge(v, attach_to)
            e2 = g.add_edge(attach_to, v)

            g.ep['capacity'][e1]  = link_capacity
            g.ep['capacity'][e2]  = link_capacity

        # recalc layout
        #self.pos = gt.fruchterman_reingold_layout(g, a=None, r=5.0, scale=None, circular=True, grid=True, t_range=None, n_iter=100)
        #self.pos = gt.fruchterman_reingold_layout(g, a=5.0, r=0.5, scale=0.1, circular=True, grid=False, t_range=None, n_iter=100)
        #self.pos = gt.radial_tree_layout(g, g.vertex(0))
        #self.draw_graph('capacity', 'visualisation/current.pdf')

        return new_comp


    def network_from_xml(self, path):
        """Load a network topology from GraphML XML file."""
        print("Loading network topology from XML:", path)

        self.graph = gt.load_graph(path)

        s = self.simulation
        g = self.graph

        # make network full-duplex
        print("Consider all connections full-duplex (=> make graph symetric)")
        edges = []
        for e in g.edges():
            #edges.append((e.source(), e.target(), g.ep.weight[e]))
            edges.append(e)

        for e in edges:
            new_edge = g.add_edge(e.target(), e.source(), add_missing=True)
            g.ep['weight'][new_edge] = g.ep['weight'][e]



        # add properties to graph needed for network simulation
        g.vertex_properties['obj'] = g.new_vertex_property("python::object")
        g.edge_properties['capacity'] = g.ep['weight'].copy()

        # dump status of edges
        #for e in g.edges():
        #    print(e, "w:", g.ep.weight[e], "c:", g.ep.capacity[e])
        #print()

        # instanciate tape-sim components from graph
        print("Instanciating components:")
        for v in g.vertices():
            print(v, g.vp.name[v], g.vp['eval'][v], g.vp['_graphml_vertex_id'][v])
            classname = g.vp.name[v].split(":")[0]
          
            # find client/node switch
            sc = g.vp.name[v].split(":")
            # ~> look for a named switch with name: NodeSwitch
            if len(sc) > 1 and sc[1] == 'NodeSwitch':
                self.nodeswitch = v
            elif len(sc) > 1 and sc[1] == 'DriveSwitch':
                self.driveswitch = v



            obj = None
            if g.vp['eval'][v]:
                obj = eval(g.vp['eval'][v])
            else:
                print(classname)
                obj = eval("%s.%s(s)" % (classname,classname))

            if obj != None:
                obj.graph = g
                obj.nodeidx = int(v)
                g.vp.obj[v] = obj
                print(" '- created:", obj)
            print()


        # rename the default nodeswitch to a more friendly name
        if self.nodeswitch != None:
            g.vp.name[self.nodeswitch] = 'Node Switch'

        if self.driveswitch != None:
            g.vp.name[self.driveswitch] = 'Drive Switch'



        name = g.vp["name"]
        weight = g.ep["weight"]

        # prepare label text
        edge_label = g.new_edge_property("string")
        gt.map_property_values(weight, edge_label, lambda x: str(x))

        # calc pos once to be used by all other graphs
        #self.pos = gt.sfdp_layout(g, K=100, C=0.1, gamma=10.0, mu=0.0)
        #self.pos = gt.sfdp_layout(g, gamma=10.0)
        #self.pos = gt.sfdp_layout(g, gamma=200.0)
        #self.pos = gt.fruchterman_reingold_layout(g, a=None, r=5.0, scale=None, circular=True, grid=True, t_range=None, n_iter=100)
        #self.pos = gt.arf_layout(g, d=5.0, a=10, dt=0.001, epsilon=1e-06, max_iter=1000)
        self.pos = gt.radial_tree_layout(g, g.vertex(0))

        # draw the network
        self.draw_graph('weight', 'visualisation/on-initialisation.pdf')


    def tape_from_xml(self, path):
        """Load a tape topology from GraphML XML file."""
        pass



    def inspect_network_topoply(self):
        """docstring for inspect_network_topoply():"""
        s = self.simulation
        g = self.graph

        g.list_properties()

        # inspect graph
        for v in g.vertices():
            print(v, "obj:", g.vp['obj'][v], " <-> ")
            print(v, "name:", g.vp['name'][v])
     

    def draw_graph(self, e_label, output, v_label='idx'):
        s = self.simulation
        g = self.graph

        if type(e_label) is str:
            ep = g.ep[e_label]
        else:
            ep = e_label

        # prepare busy fill color
        busy_fill = g.new_vertex_property('vector<double>')
        for v in g.vertices():
            if g.vp['obj'][v].has_capacity():
                busy_fill[v] = [1,1,1,1]
            else:
                busy_fill[v] = [1,0,0,0.5]

        # prepare label text
        edge_label = g.new_edge_property("string")
        # ensure strings':w
        gt.map_property_values(ep, edge_label, lambda x: str(x))


    
        # Adjust, vertex label?
        if v_label != None:
            if v_label == 'idx':
                vertex_label = g.copy_property(g.vp['name'])
                for v in g.vertices():
                    vertex_label[v] =  str(int(v)) + "::" + vertex_label[v]
            else:
                # prepare vertex label text
                if type(v_label) is str:
                    vp = g.vp[e_label]
                else:
                    vp = v_label

                vertex_label = g.new_edge_property("string")
                # ensure strings
                gt.map_property_values(vp, vertex_label, lambda x: str(x))
        else:
            vertex_label = g.vp['name']


        pos = self.pos
        gt.graph_draw(g, pos=pos,

            output_size=(800, 600),

            vertex_text=vertex_label, 
            vertex_shape = 'circle',
            #vertex_shape = 'square',
            #vertex_aspect = 2.0,
            vertex_pen_width = 0.5,
            vertex_fill_color = busy_fill, # TODO
            vertex_color = [0,0,0,1],

            vertex_text_color = [0,0,0,0.8],
            vertex_font_family = 'sans-serif',
            vertex_font_size = 10,
            vertex_font_weight = cairo.FONT_WEIGHT_BOLD,

            edge_pen_width=gt.prop_to_size(ep, mi=1, ma=15, power=1),
            edge_text=edge_label,
            edge_end_marker = 'bar',
            #edge_marker_size = 4,
            edge_font_family = 'sans-serif',
            edge_font_size = 8,
            edge_color = [0,0,0,0.2],

            output=output)
