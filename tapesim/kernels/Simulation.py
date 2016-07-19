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

    # Simulation state
    topology = None

    components = [] # component states

    clients = []    # clients
    servers = []    # I/O servers
    drives  = []    # drives
    


    # options

    def __init__(self,
            starting_time=datetime.datetime(1,1,1, microsecond=0),
            confirm_step = False,
            keep_finished = False,
            max_iterations = 100,
            report = None
        ):
       
        print("Initialising Simulation...")

        # for simplicity also have simulation member
        # allows to copy snippets from other parts more easily
        self.simulation = self

        # Simulation State
        self.last_ts = None
        self.ts = starting_time
        self.next_ts = None
        self.halted = False
        self.iteration = 0
        self.stop_time = None

        self.force_proceed_counter = 0

        # Simulation Event Provider
        self.provider = []

        # Event bookkeeping
        self.incoming   = []
        self.waiting    = []
        self.processing = []

        self.ioqueue = []
        self.netqueue = []

        self.finished   = []

        # Simulation control and termination
        self.max_iterations = max_iterations
        self.confirm_step = confirm_step
        self.keep_finished = keep_finished

        # Analysis and reporting helpers
        self.persistency = PersistencyManager.PersistencyManager() 
        self.report = Report.Report(self)

        # Various tape related controller and management facilities
        self.fc = Cache.Cache(self, size=math.pow(1024, 5)*5) # 5 PB shared disk cache
        self.fm = FileManager.FileManager(self)
        self.tm = TapeManager.TapeManager(self)
        self.rs = RobotScheduler.RobotScheduler(self) 
        self.io = IOScheduler.IOScheduler(self)

        # counter
        self.rids = 0


        self.dump_flow_history = False

        self.wait_filter = 0



        self.fieldnames = [
            'datetime',
            '1m',
            '2m',
            '3m',
            '4m',
            '5m',
            '8m',
            '10m',
            '15m',
            '20m',
            '30m',
            '1h',
            '2h',
            '4h',
            '8h',
            'more',
            'count'
        ]
        self.simulation.report.prepare_report('waiting', self.fieldnames)



        pass

    def print_status_short(self):
        """Dump internal state."""

        return

        print(" __________")
        print("/")
        print("Incoming:  ", len(self.incoming))
        print("Waiting:   ", len(self.waiting))
        print("I/O:       ", len(self.ioqueue))
        print("Network:   ", len(self.netqueue))
        print("Processing:", len(self.processing))
        print("Finished:  ", len(self.finished))
        total = 0
        total += len(self.incoming)
        total += len(self.waiting)
        total += len(self.processing)
        total += len(self.finished)
        print("Total:", total)
        print("\__________")
        print("")


    def print_status(self):
        """Dump internal state."""

        return

        print(" __________")
        print("/")
        print("iteration=%d/%d, ts=%s" % (
            self.iteration,
            self.max_iterations,
            str(self.ts)
            ))


        print("Cache:", "fill:", self.fc.size, self.fc.files)

        print("Incoming:  ", len(self.incoming))
        pprint.pprint(self.incoming)

        print("Waiting:   ", len(self.waiting))
        pprint.pprint(self.waiting)

        #print("I/O:   ", len(self.ioqueue))
        #pprint.pprint(self.ioqueue)

        #print("Network:   ", len(self.netqueue))
        #pprint.pprint(self.netqueue)

        print("Processing:", len(self.processing))
        pprint.pprint(self.processing)

        print("Finished: ", len(self.finished)) 
        pprint.pprint(self.finished)

        total = 0
        total += len(self.incoming)
        total += len(self.waiting)
        total += len(self.processing)
        total += len(self.finished)
        print("Total:", total)
        print("\__________")
        print("")




    def start(self):
        """Starts the simulation."""
        print("Simulation.start()")
        self.run()
        pass

    def run(self):
        while not self.halted:
            self.print_status_short()
            self.step()


    def suggest_next_ts(self, timestamp):
        """ Updates the timestamp thats used for the next step."""
        if self.next_ts == None or timestamp < self.next_ts:
            self.next_ts = timestamp

        print("Found next_ts:", self.next_ts)

    def consider_request_ts(self, lst):
        """ Consider requests in lst when determining next timestamp. """
        # TODO: double check when sorting is actually necessary
        if len(lst):
            lst.sort(key=lambda x: x.time_next_action)
            self.suggest_next_ts(lst[0].time_next_action)


    def step(self):
        print("Simulation.step() --------------------------------------------------------------------------------------------")
        print()

        # by now all components should have called s.suggest_next_ts()
        # only the requests are not yet considered, until...
        self.consider_request_ts(self.incoming)
        self.consider_request_ts(self.processing)
        #self.consider_request_ts(self.waiting)

        # waiting should have no activity and can be ignored
       
        # set new ts and reset next_ts to determine winner
        print("      last_ts:", self.last_ts)
        print("Found next_ts:", self.next_ts)
            
        # fetch from providers
        batch_limit = 10
        if len(self.incoming) < batch_limit:
            #print(self.provider)
            for provider in self.provider:
                #print(provider)
                provider.fetch_batch(batch_limit-len(self.incoming))

        # reconsider requests
        self.consider_request_ts(self.incoming)




        # set new ts and reset next_ts to determine winner
        print("Found next_ts:", self.next_ts)
        self.last_ts = self.ts
        self.ts = self.next_ts
        self.next_ts = None



        # force progress
        #if force_progress_counter >= 5:
        #    force_progress_coutner = 0
        #    self.ts = self.ts + datetime.timedelta(microseconds=1)


        #self.print_status()
        self.print_status_short()


        # count unfinished
        unfinished = 0
        unfinished += len(self.incoming)
        unfinished += len(self.waiting)
        unfinished += len(self.processing)

        if unfinished <= 0: 
            print("Simulation halted. Nothing to do.")
            self.halted = True
        elif self.iteration >= self.max_iterations and self.max_iterations not in ['inf', -1, None]:
            print("Simulation halted. Max iterations reached.")
            self.halted = True
        else:
            self.iteration += 1
            self.process()
            #self.print_status()
            self.print_status_short()

            # draw snapshot
            #self.topology.draw_graph('capacity', 'visualisation/current.pdf')

            # proceed to next step
            if self.confirm_step:
                user = input("Continue? [Enter]")

        self.topology.draw_graph('capacity', 'visualisation/current.pdf')

    def process_read(self, request):
        pass

    def process_write(self, request):
        pass


    def process_incoming(self):
        """docstring for process_incoming"""

        
        #print("\n>>> Handle incoming. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.incoming.sort(key=lambda x: x.time_next_action)

        #print("Incoming:")
        #pprint.pprint(self.incoming)

        while len(self.incoming):
            if self.incoming[0].time_next_action == self.ts:   # or maybe occur time?
                request = self.incoming.pop(0)
                self.analyse(request)
                self.waiting.append(request) 
                #self.finished.append(request) 
            else:
                # all elements incoming at this time have been handled
                break;
   


    def process_waiting(self, waiting=[]):
        """
        @param waiting  a list of waiting requests from other processing steps

        """


        self.report_waiting(self.waiting)
        #self.report_waiting(waiting)



        print("\n>>> Handle waiting. Allocate resources. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.waiting.sort(key=lambda x: x.time_next_action)

        print("Waiting:", len(self.waiting))
        #pprint.pprint(self.waiting)

        free_drives = []
        for drive in self.drives:
            if drive.has_capacity():
                free_drives.append(drive)

        print("Free drives:", len(free_drives))
        #free_drives)

        while len(self.waiting):
            request = self.waiting.pop(0)

            # TODO: tape drive scheduler here? network considerations?
            # TODO: make drives busy 

            #print(request.attr)

            if request.attr['analysis']['cache']:
                print("is cached! can serve directly")
                self.processing.append(request)

            elif len(free_drives) > 0:

                #print("not cached.. need drive")

                # update time_next_action and pass to next processing step
                current_drive = free_drives.pop()

                # TODO: actually do the drive and tape receival
                # drive allocation, happens already
                if request.attr['analysis']['tape']:
                    accum = request.attr['analysis']['tape']['rtime']
                    accum += request.attr['analysis']['tape']['stime'] 

                    print("rec + spool:", self.now(), "///", accum)

                    request.time_next_action = self.now() + accum

                self.processing.append(request)
            else:
                # no resources available attach to tmp_waiting
                waiting.append(request)

        self.waiting = waiting



    def process(self):
        """Process requests and reallocate resources if possible."""


        processed0 = []
        processed1 = []
        waiting = []

        # Handle incoming
        self.process_incoming()

       

        #print("\nCache:", "fill:", self.fc.size, self.fc.files)


        #print("\n>>> Handle active/processing (calc work done). Free resources. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.processing.sort(key=lambda x: x.time_next_action)

        print("Processing:")
        #pprint.pprint(self.processing)

        while len(self.processing):
            request = self.processing.pop(0)


            # CACHE guards
            if request.attr['analysis']['cache']:
                # tmp: serve instantly
                #print("CACHE PROCESSED:", request.adr())
                request.remaining = 0  # TODO: only after allocation!!!!!


            # WRITE guards
            if request.attr['type'] in ['w', 'write']:
                # tmp: finish writes immedietly
                #print("WRITE PROCESSED:", request.adr())
                request.remaining = 0  # TODO: only after allocation!!!!!

                # TODO add to tape I/O

            # READ guards
            if request.attr['analysis']['file'] == False and request.attr['type'] in ['r', 'read']:
                # can not serve read requestuest for non existing file
                #print("DROP:", request.adr())
                request.status = 'DROP'

            if request.status not in ['DROP'] and request.attr['allocation']['status'] != None: # todo change status to more approp.
                # update remaining data to be processed
                request.serve()

            
            if request.remaining <= 0.0 or request.status in ['DROP']:
                print("FINA:", request.adr())
                request.finalize()

                # keep finished?
                if self.keep_finished:
                    self.finished.append(request)
            else:
                print("not fin!!", request.remaining, " / ", request.status)
                processed0.append(request)


        print("\n>>> Reallocate resources. >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        processed0.sort(key=lambda x: x.time_occur) # NOTICE: sort by time_occur to realize FIFO

        print("Processed0:")
        #pprint.pprint(processed0)

        while len(processed0):
            request = processed0.pop(0)

            r = request.attr['analysis']

            # got tape?, find available spool times
            best_max_flow = 0
            best = {}
            if r['tape']:

                print(request.adr(), "has tape")

                if request.attr['allocation']['status'] == None: 

                    print(request.adr(), "allocation is none")

                    # no drive assigned yet consider network and drive when allocating
                    # choose best

                    analyse_limit = 4
                    for drive in self.drives:

                        if not drive.has_capacity():
                            # skip busy drives
                            continue

                        if analyse_limit < 0:
                            break 

                        analyse_limit -= 1

                        print("   '-", drive)

                        r['tape']['stime'] = drive.get_spool_time(pos=r['file']['pos'])
                        print("     '- Spool time:", r['tape']['stime'])


                        # find path from drive to client
                        src, tgt = drive.nodeidx, request.client.nodeidx


                        res, max_flow = self.topology.max_flow(src, tgt)
                        print("     '- Max-Flow:", max_flow)

                        if max_flow > best_max_flow:
                            best_max_flow = max_flow
                            best = {'max_flow': max_flow, 'res': res, 'drive': drive}

                        # shortest path
                        #vlist, elist = self.topology.get_path(src, tgt)
                        #print("      ", [str(v) for v in vlist])
                        #print("      ", [str(e) for e in elist])
    
                    #print("best-max-flow:", best_max_flow)
                    #print("best:", best)
            
                    # proceed with best and manifest the option
                    if best_max_flow > 0:
                        best['status'] = False
                        request.changed_allocation(best)

                else:
                    # reallocate more resources if available
                    # TODO)

                    # find path from drive to client
                    src = request.attr['allocation']['drive'].nodeidx
                    tgt = request.client.nodeidx

                    res, max_flow = self.topology.max_flow(src, tgt)
                    #print(request.adr(), "upgrade?     '- Max-Flow:", max_flow)
                    #print(request.__repr__(), "upgrade?     '- Max-Flow:", max_flow)

                    if best_max_flow > 0:
                        request.changed_allocation(best)
                    pass

                # allocate the proposed resources
                if request.attr['allocation']['status'] == False:
                    request.attr['allocation']['drive'].allocate_capacity()
                    self.topology.allocate_capacity(request.attr['allocation']['res'])
                    request.attr['allocation']['status'] = True
                
                # calculate next action under current allocation
                if request.attr['allocation']['status'] == True:
                    request.calc_next_action()
                    processed1.append(request)
                else:
                    #print("NO RESOURCES TO SERVE REQUEST, POSTPONE:", request)
                    waiting.append(request)

        self.processing = processed1



        # Finally handle waiting
        self.process_waiting(waiting)

    
        #print("\n>>> I/O Queue >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #print("I/O:")
        #pprint.pprint(self.ioqueue)

        #while len(self.ioqueue):
        #    request = self.ioqueue.pop() 
        #    self.finished.append(request)

        #print("\n>>> Net Queue >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #print("Net:")
        #pprint.pprint(self.netqueue)

        #while len(self.netqueue):
        #    request = self.netqueue.pop() 
        #    self.finished.append(request)




    def analyse(self, request):
        """Handle the incoming request."""
        
        analysis = {'serveable': False, 'cache': None, 'file': None, 'tape': None}

        #print("Simulation.analyse(%s)" % repr(request))

        filename = request.attr['file']

        analysis['cache'] = self.fc.lookup(filename)
        #print(" '- Cache:", analysis['cache'])

        analysis['file'] = self.fm.lookup(filename)
        #print(" '- File:", analysis['file'])

        if analysis['file']:
            # file exists, gather information on tape


            # hm what is this for?!
            #if analysis['file'] == {'pos': 0}:
            #    for f in self.fm.files:
            #        print(f, self.fm.files[f])


            analysis['tape'] = self.tm.lookup(analysis['file']['tape'])
            #print(" '- Tape:", analysis['tape'])
            analysis['tape']['rtime'] = self.rs.receive_time(analysis['tape']['slot'])
            #print("   '- Receive time:", analysis['tape']['rtime'])
        else:
            # allocate tape
            # register file
            # todo allocate filename/tape
            #self.fm.update(filename)
            # TODO: allocate file and tape for writing
            pass


        # got tape?
        #, find available spool times
        if analysis['tape']:
            print()
            analyse_limit = 4
            for drive in self.drives:
                if analyse_limit < 0:
                    break 

                analyse_limit -= 1

                #print("   '-", drive)
                analysis['tape']['stime'] = drive.get_spool_time(pos=analysis['file']['pos'])
                #print("     '- Spool time:", analysis['tape']['stime'])

        # attach analysis to request

        print("Analysis:", analysis)
        request.attr['analysis'] = analysis


    def submit(self, request):
        """Adds a job to the queue."""
        print("Simulation.submit(%s)" % repr(request))
        self.incoming.append(request)



    def now(self):
        """docstring for now"""
        return self.ts



    def report(self):
        """Prints a simple report for the finished requests."""
       
        print("\n\n\n")
        print("Report:")
        for request in self.finished:
            print(request)
            print("Took:", request.time_finished - request.time_occur)
            print("\n")


    def report_waiting(self, lst):
        """ Add the current stage count to the stages.csv with current model time. """
        print("report waiting")

        self.wait_filter += 1

        # log only every 
        if self.wait_filter % 200 != 0:
            return



        self.dic = dict.fromkeys(self.fieldnames)
        self.dic['1m']   = 0 
        self.dic['2m']   = 0 
        self.dic['3m']   = 0 
        self.dic['4m']   = 0 
        self.dic['5m']   = 0 
        self.dic['8m']   = 0 
        self.dic['10m']  = 0
        self.dic['15m']  = 0
        self.dic['20m']  = 0
        self.dic['30m']  = 0
        self.dic['1h']   = 0
        self.dic['2h']   = 0
        self.dic['4h']   = 0
        self.dic['8h']   = 0
        self.dic['more'] = 0 

        dic = self.dic

        for req in self.waiting:
            delta = self.now() - req.time_occur
            mapping = [
               (datetime.timedelta(minutes=1), '1m'),
               (datetime.timedelta(minutes=2), '2m'),
               (datetime.timedelta(minutes=3), '3m'),
               (datetime.timedelta(minutes=4), '4m'),
               (datetime.timedelta(minutes=5), '5m'),
               (datetime.timedelta(minutes=8), '8m'),
               (datetime.timedelta(minutes=10), '10m'),
               (datetime.timedelta(minutes=15), '15m'),
               (datetime.timedelta(minutes=20), '20m'),
               (datetime.timedelta(minutes=30), '30m'),
               (datetime.timedelta(hours=1), '1m'),
               (datetime.timedelta(hours=2), '2m'),
               (datetime.timedelta(hours=4), '3m'),
               (datetime.timedelta(hours=8), '4m'),
                 ]

            for m in mapping:
                if delta < m[0]:
                    dic[m[1]] += 1
                    break


        dic['datetime'] = str(self.simulation.now())
        dic['count'] = str(len(lst))

        self.simulation.report.add_report_row('waiting', dic)



    def finalize(self):
        self.fm.dump()
        #self.tm.dump()
        #self.fc.dump()
        
