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
import signal
import sys
import argparse
import pprint

import pprint
import datetime
import time

import ProviderXferlog
import RebuildFilesystem

# simulation and reporting facilities
import tapesim.Simulation as Simulation
import tapesim.Topology as Topology

# import datatypes required used in this simulation
import tapesim.datatypes.Request as Request

# import hardware components required for this example
import tapesim.components.Client as Client
import tapesim.components.Switch as Switch
import tapesim.components.IOServer as IOServer
import tapesim.components.Drive as Drive
import tapesim.components.Library as Library

# import virtual components, usually schedulers and managers (e.g. lookup tables)
import tapesim.components.Cache as Cache
import tapesim.components.FileManager as FileManager
import tapesim.components.TapeManager as TapeManager


# TODO: indented for snapshot creation on abort.
def signal_handler(signal, frame):
    print("\nTODO: dump snapshot?")
    sys.exit(0)

# register interrupt handler
signal.signal(signal.SIGINT, signal_handler)


def main():
    print()
    print("== Configuration ==")
    # maybe some environment variables?
    # print(os.environ['TAPESIM_'])





    parser = argparse.ArgumentParser(description='Simulating Tape Storage Libraries/Silos')

    #parser.add_argument('tracefile', nargs='?', type=argparse.FileType('r'), default="../assets/traces/xferlog.extract.201512.out")
    #parser.add_argument('tracefile', nargs='?', type=argparse.FileType('r'), default="../assets/traces/xferlog.extract.201512_ALTERED-FOR-TESTING-SHORT.out")
    #parser.add_argument('tracefile', nargs='?', type=argparse.FileType('r'), default="../assets/traces/xferlog.extract.201512_ALTERED-FOR-TESTING.out")
    parser.add_argument('tracefile', nargs='?', type=argparse.FileType('r'), default="data/traces/dummy.xferlog")
    parser.add_argument('--networktopoloy', default="data/configs/DKRZ.xml")
    parser.add_argument('--librarytopoloy', default="data/configs/library_DKRZ.xml")

    

    parser.add_argument('--limit', type=int, help='')
    parser.add_argument('--drives', type=int, help='')


    parser.add_argument('--config', type=int, help='')
    #parser.add_argument('--snapshot', help='')

    args = parser.parse_args()
    print(args)


    print("PID:", os.getpid())
    user = input("Continue? [Enter]")

    # Setup simulation
    print("")
    print("== Init Simulation ==")
    #sim = Simulation.Simulation(max_iterations=-1, confirm_step=True)
    sim = Simulation.Simulation(max_iterations=-1)
    #sim = Simulation.Simulation(max_iterations=-1, keep_finished=True, confirm_step=True)

    # Register Components and connect
    print("")
    print("== Prepare Topology ==")
    # load a topology from xml
    #t = Topology.Topology(s, network_xml='configs/network.xml') 
    t = Topology.Topology(sim, network_xml=args.networktopoloy) 
    sim.topology = t 



    limit = None
    #limit = 50000
    #limit = 10000
    #limit = 1000
    #limit = 1000
    #limit = 10

    
    if args.limit:
        limit = args.limit


    drives = 60
    if args.drives:
        drives = args.drives


    # rebuild filesystem
    mkfs = RebuildFilesystem.RebuildFilesystem(sim, args.tracefile, limit=limit)
    mkfs.rebuild_filesystem()

    print()
    print("Files:", len(sim.fm.files))
    for f in sim.fm.files:
        print(f, sim.fm.files[f])
    print("Tapes:", len(sim.tm.tapes))
    #pprint.pprint(sim.tm.tapes)

    # set trace file and register as provider
    trace = ProviderXferlog.ProviderXferlog(sim, args.tracefile, limit=limit)
    sim.provider.append(trace)



    # Issue some requests to be simulated.
    print()
    print("== Submit some requests ==")
    def tsu(us):
        """ Convienient microscond datetime creation. """
        return datetime.datetime(1,1,1, microsecond=us)

    def tss(s):
        """ Convienient second datetime creation. """
        return datetime.datetime(1,1,1, second=s)


    # sparse event correct timings?
    #Request.Request(s, s.clients[0], occur=tsu(10), attr={'file': 'abc', 'type': 'read', 'size': 100})
    #Request.Request(s, s.clients[0], occur=tss(20), attr={'file': 'xyz', 'type': 'write', 'size': 100})


    
    
    # add a number of tape drives
    #for i in range(1,65):
    for i in range(0,drives):
        drivename = "Drive %d" % i
        new_drive = sim.topology.register_network_component(name=drivename, link_capacity=100, drive=True)
        print("drives")


    # start the simulation
    print()
    print("== Start Simulation ============================================================================")
    print("== Start Simulation ============================================================================")
    print("== Start Simulation ============================================================================")
    sim.start()

    # Setup up report
    print()
    print("== Report ==")
    #r.write_requests(s.finished)

    # only needed to test signal handler
    # signal.pause()


    # dump hosts observed so far
    print("Trace.hosts")
    print("read:", trace.counter)
    pprint.pprint(trace.hosts)


    # dump registered components
    print()
    for c in sim.components:
        print(c)


    sim.finalize()


    pass


if __name__ == '__main__':
    # take the processing time
    start = time.clock()
    main()
    end = time.clock()
    elapsed = end - start
    print('\nProcess time:', elapsed, 'seconds')

