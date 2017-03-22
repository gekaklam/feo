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

# Data Collection and Reporting
import tapesim.SnapshotManager as SnapshotManager
import tapesim.Report as Report

# Topologies
import tapesim.Topology as Topology

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



READ = ['read', 'r', 'READ', 'R']
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
            report = None,
            debug = None
        ):

        # Enable/disable debug messages
        self.debug = False
        if debug != None:
            self.debug = debug

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
        self.persistency = SnapshotManager.SnapshotManager()
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

        self.transfer_cap = 1000



        # Reports
        #########

        # Busy Drives ~= Stages | (perdiodic, thus local extrema may remain unoticed)
        self.report_drives = 'drives'
        self.report_drives_fieldnames = ['datetime', 'free', 'enabled', 'total']
        self.report.prepare_report(self.report_drives, self.report_drives_fieldnames)

        # Request Wait-Times | (perdiodic, thus local extrema may remain unoticed)
        self.report_wait_times = 'wait-times'
        self.report_wait_times_fieldnames = ['datetime', '1m', '2m', '3m', '4m', '5m', '8m', '10m', '15m', '20m', '30m', '1h', '2h', '4h', '8h', 'more', 'count']
        self.report.prepare_report(self.report_wait_times, self.report_wait_times_fieldnames)

        pass


    def log(self, *args, level=0, tags=[], force=False, **kargs):
        # exit early? debug off?
        if self.debug == False and force == False:
            return

        if self.ts is not None:
            print("[%s]" % self.ts.strftime("%Y-%m-%d %H:%M:%S.%f"), *args, **kargs)
        elif self.last_ts is not None:
            print("[%s]" % self.last_ts.strftime("%Y-%m-%d %H:%M:%S.%f"), *args, **kargs)
        else:
            print("[%s]" % "????-??-?? ??:??:??.??????", *args, **kargs)
            #print("[%s] %s" % ("           None           ", msg))


    def suggest_next_ts(self, timestamp):
        """ Updates the timestamp thats used for the next step."""

        #print("suggest_next_ts: timestamp:", timestamp)
        #print("suggest_next_ts: next_ts:", self.next_ts)

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
        self.consider_request_ts(self.processing)
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

            if self.confirm_step:
                self.topology.draw_graph('capacity', 'visualisation/waiting-for-user-confirmation.pdf')
                user = input("Continue? [Enter]")

        elif self.iteration >= self.limit_iterations and self.limit_iterations not in ['inf', -1, None]:
            print("Simulation halted. Max iterations reached.")
            self.halted = True

            if self.confirm_step:
                self.topology.draw_graph('capacity', 'visualisation/waiting-for-user-confirmation.pdf')
                user = input("Continue? [Enter]")

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

    def get_free_drives(self):
        """Get the number of free drives for the current library topology."""
        free_drives = []
        for drive in self.drives:

            # skip busy drives
            if not drive.has_capacity():
                continue
            else:
                free_drives.append(drive)

        return free_drives

    def process_read_lifecycle(self, request):
        """Lifecycle of a READ request."""

        self.log("READ PHASE 1", request)

        if request.is_cached:
            self.log(request.adr() +  " is cached");
            self.log(" -> DISKIO")
            request.log_status("Enqueue for Disk I/O -> Client")

            #request.time_next_action = datetime.datetime(year=9999, month=12, day=31)
            request.time_next_action = self.simulation.now()
            # yield later, try allocation immedietly

        else:
            self.log(request.adr() +  " is not cached");
            self.log(" -> TAPE I/O -> Client + Cache")
            request.log_status("Enqueue for Tape I/O -> Cache/Client")

            # include 11 second tape receive panelty
            request.time_next_action = self.simulation.now() + datetime.timedelta(seconds=50)
            print("request next action:", request.time_next_action)
            self.suggest_next_ts(request.time_next_action)
            yield True



        self.log("########################")
        self.log("########################", request)
        self.log("########################")


        print(request.time_next_action)
        print(self.simulation.now())

        while self.simulation.now() < request.time_next_action:
            self.log(" not my turn yet", request)
            yield True


        # Try to get allocation
        while request.attr['allocation']['status'] == None:

            src = None
            tgt = None

            request.time_next_action = datetime.datetime(year=9999, month=12, day=31)

            if request.is_cached:
                self.log("READ: TRY ALLOCATION (cached)", request)

                src = self.fc
                tgt = request.client

                pass

            else:
                self.log("READ: TRY ALLOCATION (uncached)", request)

                free_drives = self.get_free_drives()
                self.log(free_drives)

                if len(free_drives) > 0:
                    src = free_drives[0]
                    tgt = request.client


            if src != None and tgt != None:
                # find path source to target
                res, max_flow = self.simulation.topology.max_flow(src.nodeidx, tgt.nodeidx)

                self.simulation.topology.cap_edge_property(res, self.transfer_cap)
                if max_flow > self.transfer_cap:
                    max_flow = self.transfer_cap

                print(" 'Transfer':", src, "to", tgt)
                print("     '- Max-Flow:", max_flow)
                print("     '- Res:", res)


                best = None

                if max_flow > 0:
                    # reserve resources

                    if request.is_cached:
                        best = {'max_flow': max_flow, 'res': res, 'drive': None, 'status': True}
                    else:
                        # src is a drive and needs to be blocked
                        best = {'max_flow': max_flow, 'res': res, 'drive': src, 'status': True}
                        src.allocate_capacity()





                    request.changed_allocation(best)
                    self.topology.allocate_capacity(request.attr['allocation']['res'])

                    # store allocation in request and calculate next timestep
                    request.calc_next_action()
                    #print("request next action:", request.time_next_action)
                    self.suggest_next_ts(request.time_next_action)

            yield True



        while request.remaining > 0.0:
            #print("find better allocation?")
            request.serve()
            request.calc_next_action()
            #print("request next action:", request.time_next_action)
            self.suggest_next_ts(request.time_next_action)
            yield True

        self.fc.set(name=request.attr['file'], size=request.size, modified=self.simulation.now(), dirty=False)

        # set finished
        request.time_finished = self.simulation.now()

        self.log("FINALIZE:" + request.adr())
        request.finalize()
        yield False

    def process_write_lifecycle(self, request):
        """Lifecycle of a write request."""

        print("WRITE PHASE 1", request)

        # Try to get allocation
        while request.attr['allocation']['status'] == None:

            self.log("WRITE: TRY ALLOCATION", request)

            src = None
            tgt = None

            request.time_next_action = datetime.datetime(year=9999, month=12, day=31)

            src = request.client
            tgt = self.fc

            if src is not None and tgt is not None:
                # find path source to target
                res, max_flow = self.simulation.topology.max_flow(src.nodeidx, tgt.nodeidx)

                self.simulation.topology.cap_edge_property(res, self.transfer_cap)
                if max_flow > self.transfer_cap:
                    max_flow = self.transfer_cap

                print(" 'Transfer':", src, "to", tgt)
                print("     '- Max-Flow:", max_flow)
                print("     '- Res:", res)

                best = None

                if max_flow > 0:
                    # reserve resources

                    best = {'max_flow': max_flow, 'res': res, 'drive': None, 'status': True}

                    request.changed_allocation(best)
                    self.topology.allocate_capacity(request.attr['allocation']['res'])

                    # store allocation in request and calculate next timestep
                    request.calc_next_action()
                    #print("request next action:", request.time_next_action)
                    self.suggest_next_ts(request.time_next_action)

            yield True

        while request.remaining > 0.0:
            #print("find better allocation?")
            request.serve()
            request.calc_next_action()
            #print("request next action:", request.time_next_action)
            self.suggest_next_ts(request.time_next_action)
            yield True

        self.fc.set(name=request.attr['file'], size=request.size, modified=self.simulation.now(), dirty=True)

        # set finished
        request.time_finished = self.simulation.now()


        # TODO: continue processing to make persistent on tape too
        self.log("WRITE: TRY PHASE TWO: Copy to tape.", request, force=True)


        self.log("FINALIZE:" + request.adr())
        request.finalize()
        yield False






    def process(self):
        """Process requests and reallocate resources if possible."""

        self.log("Simulation.process()")

        # TODO: update active on this timestemp requests or do we have to update more? to reflect state

        self.log()
        self.log()
        self.log()



        # maybe collect one large list of happening events
        # and handle them depending on their next decision?
        self.processing.sort(key=lambda x: x.time_occur)
        processing_handled = []
        while len(self.processing):
            request = self.processing.pop(0)

            self.log(request)
            self.log(request.attr['allocation'])
            # proceed with request handling procedure
            try:
                ret = next(request.process)

                processing_handled.append(request)

            except StopIteration:
                self.log("Process stopped:", request.adr())

                # if nothing else reattach
            self.log()
            self.log()
            self.log()

        self.processing = processing_handled


        if self.ts == datetime.datetime(year=9999, month=12, day=31):
            print("ERROR - End of time.")
            exit(1)


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
            ), force=True)

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

        free_drives = self.get_free_drives()

        print()
        self.log("Statistics:")

        # Drives
        self.log("Drives: %d/%d (Free/Total)" % (len(free_drives), len(self.drives)), force=True)


        dic = dict.fromkeys(self.report_drives_fieldnames)
        dic['datetime'] = str(self.simulation.now())
        dic['enabled'] = 0
        dic['total'] = len(self.drives)
        dic['free'] = len(free_drives)
        print(dic)
        self.simulation.report.add_report_row(self.report_drives, dic)


        # Cache
        fc = self.fc
        factor = 1024*1024*1024 # kilo * mega * giga
        factor = 1


        util = float(fc.capacity)/float(fc.max_capacity)
        free = (fc.max_capacity-fc.capacity)
        files = len(fc.files)
        dirty = fc.count_dirty()

        self.log("Cache:      %f %%  %d/%d (Remaining/Total) | (%d, %d) (Files/Dirty)" % (
            util , free/factor, fc.max_capacity/factor, files, dirty), force=True)

        pass



    def handle_performance_counters(self, mode=None):
        """
        For easy managment of performance counters, it is possible to register
        callbacks that are triggered on a regular basis:

            every x iterations
            every x seconds

        """


        pass





    # ID provision
    def get_rid(self):
        """ Request IDs """
        new_rid = self.rids
        self.rids += 1
        return new_rid

    def get_tid(self):
        """ Tranfer IDs """
        new_tid = self.tids
        self.tids += 1
        return new_tid
