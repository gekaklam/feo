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
import tapesim.Debug as debug
import tapesim.Topology as Topology
import tapesim.PersistencyManager as PersistencyManager
import tapesim.Report as Report

# import datatypes required used in this simulation
import tapesim.datatypes.Request as Request
import tapesim.datatypes.Transfer as Transfer

# import hardware components required for this example
import tapesim.components.Client as Client
import tapesim.components.Switch as Switch
import tapesim.components.IOServer as IOServer
import tapesim.components.Drive as Drive
import tapesim.components.Library as Library

# import virtual/software components
import tapesim.components.Cache as Cache
import tapesim.components.FileManager as FileManager
import tapesim.components.RAIDManager as RAIDManager
import tapesim.components.TapeManager as TapeManager

# scheduler
import tapesim.scheduling.RobotScheduler as RobotScheduler
import tapesim.scheduling.IOScheduler as IOScheduler
import tapesim.scheduling.IOScheduler as DiskIOScheduler
import tapesim.scheduling.IOScheduler as TapeIOScheduler


READ = ['read', 'r', 'WRITE', 'W']
WRITE = ['write', 'w', 'WRITE', 'W']


class Simulation(object):
    """ This simulation implements a chained request queues model to simulate
    a hierarchical tape archive with a variable disk based cache. """

    # Managing installed components and how they relate using a topology
    topology = None
    components = []  # To query component states
    clients = []     # clients
    servers = []     # I/O servers
    drives  = []     # drives


    # Event management
    events = set()
    processing = []


    # Queues
    queues = [] # list of queues?

    INCOMING = []
    OUTGOING = []
    
    DISKIO  = []
    DIRTY   = []
    TAPEIO  = []
    ROBOTS  = []

    NETWORK = []

    COMPLETE = []

    def __init__(self,
            starting_time=datetime.datetime(1,1,1, microsecond=0),
            confirm_step = False,
            keep_finished = False,
            limit_iterations = 100,
            report = None
        ):

        # Convienience
        self.simulation = self

        # Simulation state
        self.halted = False
        self.iteration = 0
        self.last_ts = None
        self.ts = starting_time
        self.next_ts = None


        # Simulation control and termination
        self.limit_iterations = limit_iterations
        self.confirm_step = confirm_step
        self.keep_finished = keep_finished
        self.dump_flow_history = False


        # Simulation Event Provider
        self.provider = []
        self.provider_batch_limit = 10

        self.rids = 0 # Requests IDs    
        self.tids = 0 # Transfer IDs    

        # Analysis and reporting helpers
        self.persistency = PersistencyManager.PersistencyManager() 
        self.report = Report.Report(self)


        # Various tape related controller and management facilities
        #self.fc = Cache.Cache(self, size=math.pow(1024, 5)*5) # 5 PB shared disk cache
        self.fc = None
        self.fm = FileManager.FileManager(self)
        self.tm = TapeManager.TapeManager(self)
        self.rs = RobotScheduler.RobotScheduler(self) 
        self.io = IOScheduler.IOScheduler(self)
        self.diskio = IOScheduler.IOScheduler(self)
        self.tapeio = IOScheduler.IOScheduler(self)


        # Counters
        # self.free_drives = 0


        # Reports
        #########
        
        # Busy Drives ~= Stages | (perdiodic, thus local extrema may remain unoticed)
        self.report_busy_drives = 'busy_drives'
        self.report_busy_drives_fieldnames = ['datetime', 'count']
        self.report.prepare_report(self.report_busy_drives, self.report_busy_drives_fieldnames)

        # Request Wait-Times | (perdiodic, thus local extrema may remain unoticed)
        self.report_wait_times = 'wait-times'
        self.report_wait_times_fieldnames = ['datetime', '1m', '2m', '3m', '4m', '5m', '8m', '10m', '15m', '20m', '30m', '1h', '2h', '4h', '8h', 'more', 'count']
        self.report.prepare_report(self.report_wait_times, self.report_wait_times_fieldnames)

        pass


    def log(self, *args, level=0, tags=[], **kargs):                                                    
        if self.ts is not None:
            print("[%s]" % self.ts.strftime("%Y-%m-%d %H:%M:%S.%f"), *args, **kargs)
        elif self.last_ts is not None:
            print("[%s]" % self.last_ts.strftime("%Y-%m-%d %H:%M:%S.%f"), *args, **kargs)
        else:
            print("[%s]" % "????-??-?? ??:??:??.??????", *args, **kargs)
            #print("[%s] %s" % ("           None           ", msg))


    def suggest_next_ts(self, timestamp):
        """ Updates the timestamp thats used for the next step."""
        if self.next_ts == None or timestamp < self.next_ts:
            self.next_ts = timestamp

        self.log("Found next_ts: " + self.next_ts.strftime("%Y-%m-%d %H:%M:%S.%f"))


    def consider_request_ts(self, lst):
        """ Consider requests in lst when determining next timestamp. """
        # TODO: double check when sorting is actually necessary
        if len(lst):
            lst.sort(key=lambda x: x.time_next_action)
            self.suggest_next_ts(lst[0].time_next_action)


    def submit(self, request):
        """Adds a job to the queue."""
        self.log("Simulation.submit(%s)" % repr(request.adr()))
        self.INCOMING.append(request)


    def start(self):
        """
        Start the simulation.
        """
        print("Simulation.start()")
        self.run()
        pass

    

    def run(self):
        """
        Step through the simulation. 
        """
        print("Simulation.run()")
        while not self.halted:
            self.step()



    def step(self):
        print("--------------------------------------------------------------")
        self.log("Simulation.step()")
        self.print_status()
       

        # Fetch new events from available providers.
        if len(self.INCOMING) < self.provider_batch_limit:
            for provider in self.provider:
                provider.fetch_batch(self.provider_batch_limit-len(self.INCOMING))

       
        # Find very next event from possible candidates.
        self.consider_request_ts(self.INCOMING)
        #self.consider_request_ts(self.OUTGOING)
        #self.consider_request_ts(self.disk_IO)
        #self.consider_request_ts(self.tape_IO)
        #self.consider_request_ts(self.robots)

        # Set new ts and reset next_ts to determine winner.
        self.last_ts = self.ts
        self.ts = self.next_ts
        self.next_ts = None

        if self.ts == None:
            self.ts = self.last_ts

        
        if len(self.INCOMING) <= 0 and len(self.processing) <= 0: 
            # TODO: Doesn't this halt the simulation to early?
            print("Simulation halted. Nothing to do.")
            self.halted = True


        elif self.iteration >= self.limit_iterations and self.limit_iterations not in ['inf', -1, None]:
            print("Simulation halted. Max iterations reached.")
            self.halted = True
        else:
            self.iteration += 1
            # proceed to next step
            if self.confirm_step:
                self.topology.draw_graph('capacity', 'visualisation/waiting-for-user-confirmation.pdf')
                user = input("Continue? [Enter]")

            # Process events on next time step.
            self.process()
            self.print_stats()

        pass



    def process_read_lifecycle(self, request):

        self.log("READ PHASE 1", request)
        
        if request.is_cached:
            self.log(request.adr() +  " is cached");
            self.log(" -> DISKIO")
            request.log_status("Enqueue for Disk I/O -> Client")

        yield True

        self.log("READ PHASE 2", request)
        yield True

        self.log("READ PHASE 3", request)
        yield True

        self.log("FINALIZE:" + request.adr())
        request.finalize()
        yield False






        # INCOMING
        # Check Type
        # Check Cache
        # Check Network

        #self.log(request.adr() + " is read");


        #    t = Transfer.Transfer(self, request, src=self.fc, tgt=request.client, size=request.size)

        #    self.DISKIO.append(request) 
        #else:
        #    self.log(request.adr() + " is not cached");
        #    request.log_status("Enqueue for Tape I/O -> Disk I/O")





        ## DISKIO 
        ##self.NETWORK.append(request) 

        ## Check Free Disk Space
        ## Check Network

        ## Allocations:
        ## IN:    Client --Network-->  I/O Server  ->  RAM Cache  -> Local Disk Cache (free)
        ##                                         ->  Global Disk Cache (Network)

        ## TAPE:  Drive  --Network-->  I/O Server  ->  RAM Cache  -> Local Disk Cache (free)
        ##                                         ->  Global Disk Cache (Network)
        #
        ## DIRTY: Cache  --Network-->  I/O Server  ->  Drive
        #
        ## All Disk I/O is currently limited only by the Network.
        ## The Disk I/O queue decides which requests may get scheduled first.

        ##self.NETWORK.append(request) 
        #print(request.attr)
        #size = request.attr['size']
        #name = request.attr['file']
        #self.fc.set(name=name, size=size, modified=self.simulation.now(), dirty=False)
        #request.log_status("Staged in Cache. (Read)")
        #pass


        #self.log(" -> DISKIO")


        #pass


    def process_write_lifecycle(self, request):

        print("WRITE PHASE 1", request)
        yield True

        print("WRITE PHASE 2", request)
        yield True

        print("WRITE PHASE 3", request)
        yield True

        self.log("FINALIZE:" + request.adr())
        request.finalize()
        yield False


        ## INCOMING
        ## Check Type
        ## Check Cache
        ## Check Network

        #self.log(request.adr() + " is write");
        ## TODO: set dirty?
        #self.log(" -> DISKIO")
        #self.DISKIO.append(request) 
        #request.log_status("Enqueue for Client -> Disk I/O")

        #t = Transfer.Transfer(self, request, src=request.client, tgt=self.fc, size=request.size)
        #print(t)
        #t.renew_allocation()
        #print(t)

        ## exists? -> create
        ## displace cache
        ## transfer client to cache

        #self.TAPEIO.append(request) 

        ##self.TAPEIO.append(request) 
        ##self.DIRTY.append(request)    
        ##self.NETWORK.append(request) 
        #
        ##  
        ## DISKIO 
        ##self.NETWORK.append(request) 

        ## Check Free Disk Space
        ## Check Network

        ## Allocations:
        ## IN:    Client --Network-->  I/O Server  ->  RAM Cache  -> Local Disk Cache (free)
        ##                                         ->  Global Disk Cache (Network)

        ## TAPE:  Drive  --Network-->  I/O Server  ->  RAM Cache  -> Local Disk Cache (free)
        ##                                         ->  Global Disk Cache (Network)
        #
        ## DIRTY: Cache  --Network-->  I/O Server  ->  Drive
        #
        ## All Disk I/O is currently limited only by the Network.
        ## The Disk I/O queue decides which requests may get scheduled first.

        #size = request.attr['size']
        #name = request.attr['file']
        #self.fc.set(name=name, size=size, modified=self.simulation.now(), dirty=True)

        #request.log_status("Staged in Cache. (Dirty)")
        #request.log_status("Completed for client.")


        #pass



    def process(self):
        """Process requests and reallocate resources if possible."""
        
        self.log("Simulation.process()")

        # TODO: update active on this timestemp requests or do we have to update more? to reflect state


        # maybe collect one large list of happening events
        # and handle them depending on their next decision?
        self.processing.sort(key=lambda x: x.time_next_action)
        processing_handled = []
        while len(self.processing):
            request = self.processing.pop(0)

            # proceed with request handling procedure
            try:
                next(request.process)
                processing_handled.append(request)
            except StopIteration:
                print("iterator is empty!")


            # if nothing else reattach

        self.processing = processing_handled



        # TODO: Hooks for callbacks to be called
        # before step, "within" step, after step

        self.log("while INCOMING")
        self.INCOMING.sort(key=lambda x: x.time_next_action)
        while len(self.INCOMING):
            if self.INCOMING[0].time_next_action == self.ts:   # or maybe occur time?
                print()
                self.log("Timestamp: match")
                request = self.INCOMING.pop(0)

                self.log(request)

                request.log_status("Received")
                request.analyse()

                # do nothing with the request :)
                #self.waiting.append(request) 


                if request.type in WRITE:
                    request.process = self.process_write_lifecycle(request)

                elif request.type in READ:
                    request.process = self.process_read_lifecycle(request)

                
                self.processing.append(request)



                #print(request.adr(), "next_action:", request.time_next_action)

                #best = {'max_flow': max_flow, 'res': res, 'drive': None}
                #request.changed_allocation(best)

                #print(request.adr(), "next_action:", request.time_next_action)


                # Only start processing request when all required allocations are granted?
               



                #self.INCOMING.append(request) 
                #self.DISKIO.append(request) 
                #self.TAPEIO.append(request) 
                #self.DIRTY.append(request) 
                #self.NETWORK.append(request) 
                #self.OUTGOING.append(request) 




                
            else:
                self.log("Timestamp: No events to process.")
                # All elements incoming at this time have been handled (list is sorted!).
                break;

        #######################################################################
        pass


    def analyse(self, request):
        """Handle the incoming request."""
        pass


    def finalize(self):
        print("Simulation.finalize()")

        self.fm.dump()
        self.tm.dump()
        self.fc.dump()


    def now(self):
        """ Return the current model time. """
        return self.ts


    

    def print_status(self):
        """
        Print a status summary of the current simulation state.
        """
        self.log(" __________")
        self.log("/")
        self.log("iteration=%d/%d, ts=%s" % (
            self.iteration,
            self.limit_iterations,
            self.ts.strftime("%Y-%m-%d %H:%M:%S.%f")
            ))
       
        self.print_queue("processing")

        self.print_queue("INCOMING")
        self.print_queue("DISKIO")
        self.print_queue("TAPEIO")
        self.print_queue("OUTGOING")
        self.print_queue("COMPLETE")

        self.log("\__________")
        self.log("")
    

    def print_queue(self, name):
        queue = getattr(self, name)
        self.log("%-10s " % (name + ":") + str(len(queue)))
        for i, request in enumerate(queue):
            self.log(request)



    def print_stats(self):

        free_drives = []
        for drive in self.drives:
            if drive.has_capacity():
                free_drives.append(drive)

        print()
        self.log("Statistics:")
        self.log("Free Drives: %d/%d" % (len(free_drives), len(self.drives)))

        fc = self.fc
        factor = 1024*1024*1024 # kilo * mega * giga
        self.log("Cached:      %d/%d (%d, %d) (Files/Dirty)" % (
            fc.remain/factor, fc.size/factor, len(fc.files), fc.count_dirty()))

        pass




    # ID provision
    def get_rid(self):
        """ Request IDs """
        new_tid = self.tids
        self.tids += 1
        return new_tid

    def get_tid(self):
        """ Tranfer IDs """
        new_tid = self.tids
        self.tids += 1
        return new_tid

