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


class RebuildFilesystem(object):
    """
    RebuildFilesystem is used to analyse a trace for files which are assumed to
    be archived in the tape system. If no mapper or position generator is provided
    the system will randomly populate tapes in the system.

    """


    def __init__(self, simulation, tracefile, limit=None):

        self.simulation = simulation

        # trace reader options
        self.limit = limit

        # trace statistics
        self.reads = 0
        self.writes = 0
        self.other = 0

        self.hosts = {}
        self.files = set()

        self.size_min = 0
        self.size_max = 0
        self.sizes = []



        #selt.fh = open(filepath, "r")
        self.tracefile = tracefile

        self.counter = 0


    def sanitize_type(self, typestring):
        READ = ['PSTO_Cmd', 'STOR_Cmd']
        WRITE = ['PRTR_Cmd', 'RETR_Cmd']

        if typestring in READ:
            return 'read'
        elif typestring in WRITE:
            # TODO: REVERT!
            #return 'write'
            return 'read'
        else:
            return 'unknown:%s' % typestring
  

    def rebuild_filesystem(self): 

        line = True
        while line:
            line = self.fetch_one()
            print(self.counter)
            print()

        # reset file position
        self.tracefile.seek(0)




    def fetch_one(self):


        #  0   1  2     3     4        5                   6                     7        8
        #  wd mon      time  year     host               file                   type     bytes
        # Tue Dec 1 00:01:11 2015 10.50.35.16 2100_ten/2084/208404_qtimer.tar PSTO_Cmd 14643200
        DATE_FORMAT = "%b %d %H:%M:%S %Y"

        line = self.tracefile.readline()
        if line == '' or (self.limit != None and self.counter >= self.limit):
            print("END OF TRACE")
            return False

            # create file

        self.counter += 1

        raw_req = line.split(' ') 
        #print(raw_req)
        
        date_string = "%s %02d %s %s" % (raw_req[1], int(raw_req[2]), raw_req[3], raw_req[4])
        timestamp = datetime.datetime.strptime(date_string, DATE_FORMAT)

        attr = {'file': None, 'type': None, 'size': None}

        # files
        #self.files.add(raw_req[6])

        attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': int(raw_req[8])}
        print(attr)
        
        return self.rebuild_file(attr)


    def rebuild_file(self, attr):
        """


        """

        # Conviently access the tape and file management of the simulation.
        fm = self.simulation.fm
        tm = self.simulation.tm


        # Is the file already present?
        f = fm.lookup(attr['file'])
        if f:
            # File already exists. Print for debug purposes.
            print(f)

        elif attr['type'] in ['read', 'r']:
            # File does not exists and this a read-like request.
            # Default for READ: Precreate file.
            print("RebuildFilesystem: NEW FILE:")
            tid, t = tm.allocate(attr['size'])   
            print("tid, t:", tid, tm.tapes[tid])

            fm.update(name=attr['file'], tape=tid, size=attr['size'])
            f = fm.lookup(attr['file'])
            print("f:", f)
        else:
            # File does not exists, but access type is non-read.
            # File may or may not reside in original system
            # Default for WRITE: Assume file is not present yet. WORM ;)
            # For Write-Once-Read-Many this seems a sensible default.
            # In case of other I/O workloads this maybe to optimisitc.
            print("RebuildFilesystem: New file but will be written.")


        # hosts
        #clienthost = raw_req[5]

        #if clienthost not in self.hosts.keys():
        #    new_client = self.simulation.topology.register_network_component(name=clienthost, link_capacity=1000)
        #    self.hosts[clienthost] = new_client
   
        # TODO set correct size again
        #attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': int(raw_req[8])}
        #attr = {'file': raw_req[6], 'type': self.sanitize_type(raw_req[7]), 'size': 500}

        # Request is automatically registered with simulation
        #req = Request.Request(self.simulation, self.hosts[clienthost], occur=timestamp, attr=attr)

        return True

    def report(self):
        print("Reads:  ", self.reads) 
        print("Writes: ", self.writes) 
        print("Other:  ", self.other) 
        print("Total:  ", self.reads + self.writes + self.other)
        print("Hosts:  ", len(self.hosts)) 
        print("Files:  ", len(self.files)) 

        print()
        print("Size(min):", size_min)
        print("Size(max):", size_max) 



