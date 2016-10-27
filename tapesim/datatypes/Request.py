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
import pprint


READ = ['read', 'r', 'WRITE', 'W']
WRITE = ['write', 'w', 'WRITE', 'W']

class Request(object):
    """
    Requests are used to 
    """

    def __init__(self, simulation=None, client=None, occur=None, size=None, attr={}):
        self.simulation = simulation
        self.client = client

        self.id = simulation.get_rid()

        # Request state.
        self.type = None
        self.size = None
        self.remaining = None
        self.is_cached = False
        self.persistend = None
        self.action = None

        self.status = ''
        self.tags = set()
        self.status_log = []

        self.filename = attr['file']

        self.write_status = None

        self.process = None


        # All about time.
        self.time_occur = None        # When did the request occur/reach the I/O server?
        self.time_finished = None     # Time when the request is served as far as the client is concerned.  LEGACY
        self.time_served = None       # As far as user/clients are concerend.
        self.time_completed = None    # As far as the storage system is concerned. So this includes async activities.
        self.time_wait = None         # Accumulated wait time.
        self.time_next_action = None  # When does this request changes state the next time.
                                      #  May vary as transfer speed changes.

        if occur:
            self.time_occur = occur
        elif self.simulation != None:
            self.time_occur = simulation.now()  # should be true for most cases?
        else:
            print("Warning: free-floating request.")

        # Used by the simulation to determine next timestep.
        self.time_next_action = self.time_occur


        # Populate attr for unstable and experimental request properties.
        self.attr = attr

        self.attr['analysis'] = None
        self.attr['allocation'] = {'status': None}
    


        # Unpack attr to stable request properties.
        # Add attributes used during book-keeping.
        self.size = attr['size']
        self.remaining = attr['size']
        self.type = attr['type']

        # Network allocations related to this request. Required to free allocations later.
        # actually this sounds wrong? flows are not used for freeing
        self.flows = []

        # Make this request known to the simulation.
        #simulation.tids += 1

        if simulation != None:
            simulation.submit(self)

        pass





    def wait_for(self, dependancy):

        pass



    def print_status_log(self):
        print()
        print("Status log for", self.adr())
        for i, entry in enumerate(self.status_log):
            print(" '- Status %d:" % i, entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S.%f"), entry['msg'])
        print()


    def log_status(self, msg):
        self.simulation.log(self.adr(), "LOG STATUS:", msg)
        self.status_log.append({"timestamp": self.simulation.now(), "msg": msg})

        self.print_status_log()


    # Debug auxiliary
    ###########################################################################
    def log(self, *args, level=0, tags=[], **kargs):                                                    
        self.simulation.log("[%s]" % self.__class__.__name__, *args, **kargs)




    def changed_allocation(self, best):
        print(self.adr(), "changed allocation")

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
        """ Update the remaining bytes to be send. """

        self.log("SERVING")

        if now == None:
            now = self.simulation.now()

        if last == None:
            last = self.simulation.last_ts

        duration = now - last 
        #print(self.adr(), "serve duration:", str(duration))

        if duration.total_seconds() > 0.0:
            # TODO: variable serve rate
            bytes_served = (duration.total_seconds() + (duration.microseconds/1000000)) * (self.attr['allocation']['max_flow'] * 1024*1024) # to MB to bytes
            print("remain:", self.remaining)
            self.remaining -= bytes_served
            print(self.adr(), "bytes_served:", bytes_served)
            print("remain:", self.remaining)
        else:
            print("SHORT duration!!!")

    
        if self.remaining < 1:
            self.remaining = 0


        self.flows.append({
            'max_flow': self.attr['allocation']['max_flow'], 
            'time': self.simulation.now()
            })



    def calc_next_action(self):
        """
        Calculate when the next status change will happen for this request.
        """

        microseconds = 0

        if self.attr['allocation']['status'] != None:

            print("remaining:", self.remaining, "@ rate of:", self.attr['allocation']['max_flow']*1024*1024)

            seconds = self.remaining / (self.attr['allocation']['max_flow'] * 1024*1024)
            microseconds = seconds*1000000

        duration = datetime.timedelta(microseconds=microseconds)
        print("duration:", duration)


        if duration <= datetime.timedelta(0):
            self.remaining = 0



        self.time_next_action = self.simulation.now() + duration
        #self.time_next_action += datetime.timedelta(microseconds=1000000-self.time_next_action.microsecond)  # WHY!?

        print("Next action:", self.time_next_action, self.adr())


    def finalize(self, time=None):
        """
        Finalize request. Set done time.
        """

        self.flows.append({
            'max_flow': 0, 
            'time': self.simulation.now()
            })

        # mark file as cached
        # TODO: read vs. write?
        #if self.attr['type'] in ['w', 'write']:
        #    self.simulation.fc.set(name=self.attr['file'], modified=self.simulation.now(), persistent=False)
        #else:
        #    self.simulation.fc.set(name=self.attr['file'], modified=self.simulation.now())


        # free any allocations
        if self.status not in ['DROP'] and self.attr['allocation']['status']:
            # free network
            res = self.attr['allocation']['res']
            self.simulation.topology.free_capacity(res)

            # free drives
            if self.attr['allocation']['drive'] != None:
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

    def dump_analysis(self):
        """Make snapshot of the file system state."""
        print("")
        #self.simulation.log("")
        

    def analyse(self):
        """
        Handle the incoming request.
        
        1. Is the file cached?
        2. Is the file existing in the FileManager?
        3. Is the tape 
        
        """
       
        request = self # TODO: clean

        analysis = {'serveable': False, 'cache': None, 'file': None, 'tape': None}

        filename = self.attr['file']

        analysis['cache'] = self.simulation.fc.lookup(filename)
        analysis['file'] = self.simulation.fm.lookup(filename)

        if analysis['file']:
            # The file exists, gather information on tape.
            analysis['tape'] = self.simulation.tm.lookup(analysis['file']['tape'])
            analysis['tape']['rtime'] = self.simulation.rs.receive_time(analysis['tape']['slot'])
        else:
            # allocate tape
            request.actions = ["ALLOCATE TAPE", "REGISTER FILE"]
            #self.fm.update(filename)

        if analysis['tape']:
            # A tape is associeted with this file.
            pass

            # analysis['tape']['stime'] = drive.get_spool_time(pos=analysis['file']['pos'])
            # print("     '- Spool time:", analysis['tape']['stime'])

        # Attach analysis to request
        print("Analysis:", analysis)
        request.attr['analysis'] = analysis

        if analysis['cache'] != False:
            self.is_cached = True
        else:
            self.is_cached = False


    def __str__(self):
        return self.__repr__()


    def __repr__(self):
        adr = hex(id(self))
        info = ''
        info += self.type[:3] + ' '
        info += self.attr['file']
        info += ' @ ' +         self.time_occur.strftime("%Y-%m-%d %H:%M:%S.%f")
        #info += ' next ' +    self.time_next_action.strftime("%Y-%m-%d %H:%M:%S.%f")

        if self.time_next_action != None:
            info += ' -> ' +    self.time_next_action.strftime("%H:%M:%S.%f")
        else:
            info += ' -> ' + "ASAP"


        info += " BYTES REMAINING: " + "%s" % str(self.remaining)
        #info += " ALLOC: " + str(self.attr['allocation'])
        info += " STATUS: " + str(self.status)
        #info += str(self.attr)

        rid = ''
        if self.id != None:
            rid = self.id

        #return '<%s %s %04d: %s>' % (adr, self.__class__.__name__, rid, info)
        return '<%s %04d: %s>' % (self.__class__.__name__, rid, info)

    def adr(self):
        adr = hex(id(self))
        info = ''
        info += self.type + ' '
        info += '@ ' +         self.time_occur.strftime("%Y-%m-%d %H:%M:%S.%f")
        #return '<%s %s: %s>' % (adr, self.__class__.__name__, info)
        rid = ''
        if self.id != None:
            rid = self.id
        return '<%s %04d: %s>' % (self.__class__.__name__, rid, info)

   

        
