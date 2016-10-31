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


import time
import argparse
import sys
import os
import re
import datetime
import random
import pprint

# import datatypes required used in this simulation
import tapesim.components.Component
import tapesim.datatypes.Request as Request


#class ProviderXferlog(object):
class ProviderXferlog(tapesim.components.Component.Component):
    """ """
    #  0  1   2    3     4        5                  6                      7        8
    #  wd mon      time  year     host               file                   type     bytes
    # Tue Dec 1 00:01:11 2015 10.50.35.16 2100_ten/2084/208404_qtimer.tar PSTO_Cmd 14643200



    def __init__(self, simulation, tracefile, limit=None, client_link_capacity=1000):
        
        self.simulation = simulation

        # Configuration
        self.limit = limit
        self.tracefile = tracefile

        # Statistics
        self.counter = 0
        self.hosts = {}
        self.size_min = 0
        self.size_max = 0
        self.sizes = []


        self.client_link_capacity = client_link_capacity


    def sanitize_type(self, typestring):
        """
        Ensure xferlog types are mapped to READ and WRITE types known by the simulation.
        """

        READ = ['PSTO_Cmd', 'STOR_Cmd']
        WRITE = ['PRTR_Cmd', 'RETR_Cmd']

        if typestring in READ:
            return 'read'
        elif typestring in WRITE:
            #return 'read'
            return 'write'
        else:
            return 'unknown:%s' % typestring
  

    def fetch_batch(self, num=10): 
        """
        Fetch multiple new events from the trace but ensure to fetch all
        events when multiple events occur at teh same time.

        Parameters
        ----------
        num : max number of elements to fetch (except for cases with simultanous events)

        """
        self.log("ProviderXferlog.fetch(): %d" % num)

        # Fetch num events and keep last event to check timestamp
        # Note: fetch_one will auto-submit to simulation
        last = None
        for i in range(0,num):
            last = self.fetch_one()
            
            if last == None:
                # EOT
                return

        # keep fetching until new timestamp occurs
        if last != None:
            current = last

            while last.time_occur == current.time_occur:
                last = current
                current = self.fetch_one()
                if current == None:
                    return


    def fetch_one(self):
        """
        Fetch exactly new element from the trace file and submit to the simulation.
        """

        # Template to parse xferlog entry:
        #  0  1   2    3     4        5                  6                      7        8
        #  wd mon      time  year     host               file                   type     bytes
        # Tue Dec 1 00:01:11 2015 10.50.35.16 2100_ten/2084/208404_qtimer.tar PSTO_Cmd 14643200
        DATE_FORMAT = "%b %d %H:%M:%S %Y"

        # Check EOT.
        line = self.tracefile.readline()
        if line == '' or (self.limit != None and self.counter >= self.limit):
            self.log("END OF TRACE")
            return None

        # Keep track of events provided.
        self.counter += 1

        # Parse raw event string.
        raw_req = line.split(' ') 
        date_string = "%s %02d %s %s" % (raw_req[1], int(raw_req[2]), raw_req[3], raw_req[4])
        timestamp = datetime.datetime.strptime(date_string, DATE_FORMAT)
        attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': int(raw_req[8])}

        # Maintain a list of known hosts, register unkown hosts to topology.
        clienthost = raw_req[5]
       
        # TODO: Too many hosts fix: Max-Flow will become to costly for many hosts. 
        # Quickfix: Map every host randomly to one of only 10 possible hosts.
        self.log("Hosts: %d" % len(self.hosts.keys()))
        #clienthost = "%s" % (random.randint(1,10))

        if clienthost not in self.hosts.keys():
            self.log("Client not present.")

            new_client = self.simulation.topology.register_network_component(name=clienthost, link_capacity=self.client_link_capacity)
            self.hosts[clienthost] = new_client

        # Create actual Request-object
        req = Request.Request(self.simulation, self.hosts[clienthost], occur=timestamp, attr=attr)

        return req


    def report(self):
        self.log("Trace.counter=%d" % self.counter)
        self.log("Trace.hosts")
        pprint.pprint(self.hosts)


