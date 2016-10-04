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
import tapesim.components.Component
import tapesim.datatypes.Request as Request


class RebuildFilesystem(tapesim.components.Component.Component):
    """
    RebuildFilesystem is used to analyse a trace for files which are assumed to
    be archived in the tape system. If no mapper or position generator is provided
    the system will randomly populate tapes in the system.
    """


    def __init__(self, simulation, tracefile, limit=None):

        self.simulation = simulation

        # Configuration
        self.limit = limit
        self.tracefile = tracefile

        # Statistics
        self.counter = 0
        self.reads = 0
        self.writes = 0
        self.other = 0
        self.hosts = {}
        self.files = set()
        self.size_min = 0
        self.size_max = 0
        self.sizes = []


    def sanitize_type(self, typestring):
        READ = ['PSTO_Cmd', 'STOR_Cmtapesim.components.Component.Componentd']
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
        """Populate the tape and file system index."""

        line = True
        while line:
            line = self.fetch_one()
            self.log(self.counter)
            print()

        # Reset file position.
        self.tracefile.seek(0)


    def fetch_one(self):
        """Fetch one event from trace."""

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

        self.log(attr)
        
        return self.rebuild_file(attr)


    def rebuild_file(self, attr):
        """
        Filter and 

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
            # Default for READ: Precreate file. "Who accesses non existing files?"
            self.log("RebuildFilesystem: NEW FILE:")

            # Get a tape allocation.
            tid, t = tm.allocate(attr['size'])   
            self.log("tid, t:", tid, tm.tapes[tid])

            # Register the file to the file system index.
            fm.update(name=attr['file'], tape=tid, size=attr['size'])
            f = fm.lookup(attr['file'])
            self.log("f:", f)

        else:
            # File does not exists, but access type is non-read.
            # File may or may not reside in original system
            # Default for WRITE: Assume file is not present yet. WORM ;)
            # For Write-Once-Read-Many this seems a sensible default.
            # In case of other I/O workloads this maybe to optimisitc.
            self.log("RebuildFilesystem: New file but will be written.")

        return True


    def report(self):
        self.log("Reads:  ", self.reads) 
        self.log("Writes: ", self.writes) 
        self.log("Other:  ", self.other) 
        self.log("Total:  ", self.reads + self.writes + self.other)
        self.log("Hosts:  ", len(self.hosts)) 
        self.log("Files:  ", len(self.files)) 

        self.log()
        self.log("Size(min):", size_min)
        self.log("Size(max):", size_max) 



