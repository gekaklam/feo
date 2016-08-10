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

import datetime


class Request(object):

    simulation = None
    client = None

    attr = {}
    time_occur  = None
    time_next_action  = None
    time_finished = None
    time_wait = None # accumulated wait time

    remaining = None
    
    persistend = False

    status = ''
    tags = set()


    def __init__(self, simulation=None, client=None, occur=None, attr={}):
        self.simulation = simulation
        self.client = client

        # populate request occurence
        if occur:
            self.time_occur = occur
        elif self.simulation != None:
            self.time_occur = simulation.now()  # should be true for most cases?
        else:
            print("Warning: free-floating request.")


        self.id = simulation.rids
        simulation.rids += 1

        # Used by the simulation to determine next timestep.
        self.time_next_action = self.time_occur

        # Populate attr.
        self.attr = attr

        # Add attributes used during book-keeping.
        self.remaining = self.attr['size']
        
        self.attr['analysis'] = None
        self.attr['allocation'] = {'status': None}

        # Keep track of network allocations related to this request.
        self.flows = []

        # Make this request known to the simulation.
        if simulation != None:
            simulation.submit(self)

        pass


    def changed_allocation(self, best):
        #print(self.adr(), "changed allocation")

        #print("EXISTING ALLOC", self.__repr__()) 

        if self.attr['allocation']['status'] == None:
            self.attr['allocation'] = best

        else:
            # remember old allocations
            res = self.attr['allocation']['res']
            max_flow = self.attr['allocation']['max_flow']
            # overwrite with allocations 
            self.attr['allocation'] = best
            # merge allocaitons 
            self.attr['allocation']['max_flow'] += max_flow
            for e in self.simulation.topology.graph.edges():
                self.attr['allocation']['res'][e] += res[e]

        self.flows.append({
            'max_flow': self.attr['allocation']['max_flow'], 
            'time': self.simulation.now()
            })


    def serve(self, now=None, last=None):
        if now == None:
            now = self.simulation.now()

        if last == None:
            last = self.simulation.last_ts

        duration = now - last 
        #print(self.adr(), "serve duration:", str(duration))

        if duration.total_seconds() > 0.0:
            # TODO: variable serve rate
            bytes_served = (duration.total_seconds() + (duration.microseconds/1000000)) * (self.attr['allocation']['max_flow'] * 1024*1024) # to MB to bytes
            self.remaining -= bytes_served
            #print(self.adr(), "bytes_served:", bytes_served)

    
        if self.remaining < 1:
            self.remaining = 0


        self.flows.append({
            'max_flow': self.attr['allocation']['max_flow'], 
            'time': self.simulation.now()
            })



    def calc_next_action(self):
        seconds = self.remaining / (self.attr['allocation']['max_flow'] * 1024*1024)
        #print("secs:", seconds)
        microseconds = seconds*1000000
        #print("microsecs:", microseconds)
        duration = datetime.timedelta(microseconds=microseconds)
        #duration = datetime.timedelta(seconds=microseconds)
        #print("duration:", duration, "seconds:", seconds)
        #print("sim.now(): ", self.simulation.now())
        self.time_next_action = self.simulation.now() + duration
        self.time_next_action += datetime.timedelta(microseconds=1000000-self.time_next_action.microsecond)
        #print("Next action:", self.time_next_action)


    def finalize(self, time=None):
        """Finalize request. Set done time."""

        self.flows.append({
            'max_flow': 0, 
            'time': self.simulation.now()
            })

        # mark file as cached
        # TODO: read vs. write?
        if self.attr['type'] in ['w', 'write']:
            self.simulation.fc.set(name=self.attr['file'], modified=self.simulation.now(), persistent=False)
        else:
            self.simulation.fc.set(name=self.attr['file'], modified=self.simulation.now())


        # free any allocations
        if self.status not in ['DROP'] and self.attr['allocation']['status']:
            # free network
            res = self.attr['allocation']['res']
            self.simulation.topology.free_capacity(res)

            # free drives
            self.attr['allocation']['drive'].free_capacity()

        # set finalize timestamp
        if time == None:
            self.time_finished = self.simulation.now()
        else:
            self.time_finished = time

        # flush data
        if self.status not in ['DROP']:
            if self.simulation.dump_flow_history:
                self.simulation.report.write_request_flow_history(self)
            pass


        self.simulation.report.write_requests([self])


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        adr = hex(id(self))
        info = ''
        info += self.attr['type'] + " "
        info += self.attr['file']
        info += ' @ ' +         self.time_occur.strftime("%Y-%m-%d %H:%M:%S.%f")
        info += ' next ' +    self.time_next_action.strftime("%Y-%m-%d %H:%M:%S.%f")
        info += " BYTES REMAINING: " + "%s" % str(self.remaining)
        #info += " ALLOC: " + str(self.attr['allocation'])
        info += " STATUS: " + str(self.status)
        #info += str(self.attr)

        rid = ''
        if self.id != None:
            rid = self.id

        return '<%s %s %s: %s>' % (adr, self.__class__.__name__, rid, info)

    def adr(self):
        adr = hex(id(self))
        info = ''
        return '<%s %s: %s>' % (adr, self.__class__.__name__, info)

   

        
