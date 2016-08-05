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


import os
import sys
import datetime
import math

import pprint
import graph_tool.all as gt


# simulation and reporting facilities
import tapesim.Topology as Topology
import tapesim.PersistencyManager as PersistencyManager
import tapesim.Report as Report

# import datatypes required used in this simulation
import tapesim.datatypes.Request as Request

# import hardware components required for this example
import tapesim.components.Client as Client
import tapesim.components.Switch as Switch
import tapesim.components.IOServer as IOServer
import tapesim.components.Drive as Drive
import tapesim.components.Library as Library

# import virtual components
import tapesim.components.Cache as Cache
import tapesim.components.FileManager as FileManager
import tapesim.components.RAIDManager as RAIDManager
import tapesim.components.TapeManager as TapeManager

# scheduler
import tapesim.scheduling.RobotScheduler as RobotScheduler
import tapesim.scheduling.IOScheduler as IOScheduler




class Simulation(object):
    """ This simulation implements a chained request queues model to simulate
    a hierarchical tape archive with a variable disk based cache. """

    # Managing installed components and how they relate using a topology
    topology = None
    components = []  # To query component states
    clients = []     # clients
    servers = []     # I/O servers
    drives  = []     # drives

    # Queues
    IN = []
    OUT = []
    
    diskIO = []
    disk_dirty = []
    tapeIO = []
    robots = []

    network = []

    def __init__(self,
            starting_time=datetime.datetime(1,1,1, microsecond=0),
            confirm_step = False,
            keep_finished = False,
            max_iterations = 100,
            report = None
        ):

        # Simulation state
        self.ts = starting_time
        self.halted = False
        self.iteration = 0

        # Simulation control and termination
        self.max_iterations = max_iterations
        self.confirm_step = confirm_step
        self.keep_finished = keep_finished

        # Simulation Event Provider
        self.provider = []
        self.provider_batch_limit = 10
        self.rids = 0 # request IDs    def process_read(self, request):

        # Analysis and reporting helpers
        self.persistency = PersistencyManager.PersistencyManager() 
        self.report = Report.Report(self)




        # Various tape related controller and management facilities
        self.fc = Cache.Cache(self, size=math.pow(1024, 5)*5) # 5 PB shared disk cache

        self.fm = FileManager.FileManager(self)
        self.tm = TapeManager.TapeManager(self)
        self.rs = RobotScheduler.RobotScheduler(self) 
        self.io = IOScheduler.IOScheduler(self)

        pass

    def submit(self, request):
        """Adds a job to the queue."""
        print("Simulation.submit(%s)" % repr(request))
        self.IN.append(request)



    def start(self):
        """Starts the simulation."""
        print("Simulation.start()")
        self.run()
        pass

    def run(self):
        print("Simulation.run()")
        while not self.halted:
            self.step()



    def step(self):
        print("Simulation.step()")

        # Fetch new events from available providers
        if len(self.IN) < self.provider_batch_limit:
            for provider in self.provider:
                provider.fetch_batch(self.provider_batch_limit-len(self.IN))
        

        if self.IN <= 0: 
            print("Simulation halted. Nothing to do.")
            self.halted = True
        elif self.iteration >= self.max_iterations and self.max_iterations not in ['inf', -1, None]:
            print("Simulation halted. Max iterations reached.")
            self.halted = True
        else:
            self.iteration += 1
            
            # proceed to next step
            if self.confirm_step:
                user = input("Continue? [Enter]")


        pass


    def process(self):
        """Process requests and reallocate resources if possible."""
        pass


    def analyse(self, request):
        """Handle the incoming request."""
        pass

    def finalize(self):
        self.fm.dump()
        #self.tm.dump()
        #self.fc.dump()
        
