#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import argparse
import sys
import os
import re
import datetime
import random
# import datatypes required used in this simulation
import tapesim.datatypes.Request as Request


class ProviderXferlog(object):
    def __init__(self, simulation, tracefile, limit=None):

        self.simulation = simulation

        # trace reader options
        self.limit = limit



        self.hosts = {}

        self.size_min = 0
        self.size_max = 0
        self.sizes = []

        #  0   1  2     3     4        5                   6                     7        8
        #  wd mon      time  year     host               file                   type     bytes
        # Tue Dec 1 00:01:11 2015 10.50.35.16 2100_ten/2084/208404_qtimer.tar PSTO_Cmd 14643200

        #selt.fh = open(filepath, "r")
        self.tracefile = tracefile

        self.counter = 0
        # init



    def sanitize_type(self, typestring):
        READ = ['PSTO_Cmd', 'STOR_Cmd']
        WRITE = ['PRTR_Cmd', 'RETR_Cmd']

        if typestring in READ:
            return 'read'
        elif typestring in WRITE:
            #return 'read'
            return 'write'
        else:
            return 'unknown:%s' % typestring
  

    def fetch_batch(self, size=10): 
     
        print("fetch: ", size)

        last = None
        for i in range(0,size):
            last = self.fetch_one()

        if last != None:
            current = last

            while last.time_occur == current.time_occur:
                last = current
                current = self.fetch_one()
                if current == None:
                    return


    def fetch_one(self):
        DATE_FORMAT = "%b %d %H:%M:%S %Y"

        line = self.tracefile.readline()
        if line == '' or (self.limit != None and self.counter >= self.limit):
            print("END OF TRACE")
            return None


        self.counter += 1

        raw_req = line.split(' ') 
        #print(raw_req)

        
        date_string = "%s %02d %s %s" % (raw_req[1], int(raw_req[2]), raw_req[3], raw_req[4])
        timestamp = datetime.datetime.strptime(date_string, DATE_FORMAT)

        attr = {'file': None, 'type': None, 'size': None}

        # hosts
        clienthost = raw_req[5]
       
        # TODO: to many hosts fix
        print("Hosts:", len(self.hosts.keys()))
        clienthost = "%s" % (random.randint(1,10))

        if clienthost not in self.hosts.keys():

            print("NOT!!")

            new_client = self.simulation.topology.register_network_component(name=clienthost, link_capacity=1000)
            self.hosts[clienthost] = new_client
   
        # TODO set correct size again
        attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': int(raw_req[8])}
        #attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': 50000000000}
        #attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': 500}

        # Request is automatically registered with simulation
        req = Request.Request(self.simulation, self.hosts[clienthost], occur=timestamp, attr=attr)

        return req



