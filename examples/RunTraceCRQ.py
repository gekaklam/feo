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


import sys
import os
import signal
import argparse
import pprint

import pprint
import datetime
import time
import locale
locale.setlocale(locale.LC_ALL, 'en_US')


# add parent directy as python path to allow examples to work without installing
sys.path.insert(0, "../")


import tapesim.workloads.ProviderXferlog as ProviderXferlog
import tapesim.workloads.RebuildFilesystem as RebuildFilesystem

# simulation and reporting facilities
#import tapesim.kernels.Simulation as Simulation
import tapesim.kernels.ChainedRequestQueues as Simulation
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




    parser = argparse.ArgumentParser(
        description='Simulating Tape Storage Libraries/Silos using the CRQ kernel. Chained Request Queues uses dedicated queues for Waiting Request, Disk I/O, Dirty Files, Tape I/O and Robots as well as IN and OUT going network traffic.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )


    parser.add_argument('tracefile', nargs='?', type=argparse.FileType('r'), default="../data/traces/dummy.xferlog")

    parser.add_argument('--network-topoloy', default="../data/topologies/dummy-network.xml")
    parser.add_argument('--library-topoloy', default="../data/topologies/dummy-library.xml")


    parser.add_argument('--limit', type=int, help='', default=None)
    parser.add_argument('--limit-iterations', type=int, help='', default=-1)

    parser.add_argument('--drives', type=int, help='')
    parser.add_argument('--config', type=int, help='')
    #parser.add_argument('--snapshot', help='')


    parser.add_argument("--confirm-step", help="Manually step through the simulation.", action="store_true")


    args = parser.parse_args()
    print(args)


    print("PID:", os.getpid())
    user = input("Continue? [Enter]")

    
    print()
    print("==================================================================")
    print("== Initialize Simulation =========================================")
    print("==================================================================")
    sim = Simulation.Simulation(limit_iterations=args.limit_iterations, confirm_step=args.confirm_step)


    ###########################################################################
    # Register Components and connect
    ###########################################################################
    print()
    print("==================================================================")
    print("== Prepare Topology ==============================================")
    print("==================================================================")
    # load a topology from xml
    #t = Topology.Topology(s, network_xml='configs/network.xml') 
    t = Topology.Topology(sim, network_xml=args.network_topoloy) 
    sim.topology = t 

    # Set provider limit (how many requests to process).
    limit = None
    if args.limit:
        limit = args.limit

    # Set number of drives
    drives = 60
    if args.drives:
        drives = args.drives


    # Rebuild tape filesystem: 
    mkfs = RebuildFilesystem.RebuildFilesystem(sim, args.tracefile, limit=None)
    mkfs.rebuild_filesystem()

    print()
    print("Files:", len(sim.fm.files))
    for f in sim.fm.files:
        print(f, sim.fm.files[f])
    print("Tapes:", len(sim.tm.tapes))
    #pprint.pprint(sim.tm.tapes)

    # Open tracefile and register provider
    trace = ProviderXferlog.ProviderXferlog(sim, args.tracefile, limit=limit)
    sim.provider.append(trace)

    
    
    print()
    print("==================================================================")
    print("== Install Components ============================================")
    print("==================================================================")
    
    # Install a number of tape drives.
    drives = [
			# IBM-LTO4:
			{"type": "LTO-4", "mode": "rw", "position": (0,10,1,0)},
			{"type": "LTO-4", "mode": "rw", "position": (0,10,1,3)},
			{"type": "LTO-4", "mode": "rw", "position": (0,11,1,0)},
			{"type": "LTO-4", "mode": "rw", "position": (0,11,1,3)},

			{"type": "LTO-4", "mode": "w", "position": (2,2,1,0)},
			{"type": "LTO-4", "mode": "w", "position": (2,2,1,3)},
			{"type": "LTO-4", "mode": "w", "position": (2,2,1,15)},

			# IBM-LTO5:
			{"type": "LTO-5", "mode": "rw", "position": (0,5,1,1)},
			{"type": "LTO-5", "mode": "rw", "position": (0,5,1,2)},
			{"type": "LTO-5", "mode": "rw", "position": (0,5,1,13)},
			{"type": "LTO-5", "mode": "rw", "position": (0,6,1,0)},
			{"type": "LTO-5", "mode": "rw", "position": (0,6,1,4)},
			{"type": "LTO-5", "mode": "rw", "position": (0,6,1,8)},
			{"type": "LTO-5", "mode": "rw", "position": (0,6,1,12)},
			{"type": "LTO-5", "mode": "rw", "position": (0,7,1,6)},
			{"type": "LTO-5", "mode": "rw", "position": (0,7,1,7)},
			{"type": "LTO-5", "mode": "rw", "position": (0,7,1,11)},

			# IBM-LTO6:
			{"type": "LTO-6", "mode": "rw", "position": (1,1,1,4)},
			{"type": "LTO-6", "mode": "rw", "position": (1,1,1,8)},
			{"type": "LTO-6", "mode": "rw", "position": (1,1,1,12)},
			{"type": "LTO-6", "mode": "rw", "position": (1,2,1,8)},
			{"type": "LTO-6", "mode": "rw", "position": (1,2,1,12)},
			{"type": "LTO-6", "mode": "rw", "position": (1,3,1,4)},
			{"type": "LTO-6", "mode": "rw", "position": (1,3,1,8)},
			{"type": "LTO-6", "mode": "rw", "position": (1,3,1,12)},
			{"type": "LTO-6", "mode": "rw", "position": (1,5,1,4)},

			{"type": "LTO-6", "mode": "rw", "position": (1,6,1,4)},
			{"type": "LTO-6", "mode": "rw", "position": (1,6,1,8)},
			{"type": "LTO-6", "mode": "rw", "position": (1,7,1,4)},
			{"type": "LTO-6", "mode": "rw", "position": (1,7,1,8)},

			{"type": "LTO-6", "mode": "w", "position": (2,3,1,14)},
			{"type": "LTO-6", "mode": "w", "position": (2,3,1,15)},
    ]

    for i,d  in enumerate(drives):
        #drivename = "%s Drive %d" % (d["type"], i)
        drivename = "%s" % (d["type"])
        new_drive = sim.topology.register_network_component(
                name=drivename, 
                link_capacity=100, 
                drive=True
            )


    sim.topology.draw_graph('capacity', 'visualisation/after-installation.pdf')


    print()
    print("==================================================================")
    print("== Start Simulation ==============================================")
    print("==================================================================")
    # Start the simulation.
    sim.start()

    sim.topology.draw_graph('capacity', 'visualisation/on-termination.pdf')

    print()
    print("==================================================================")
    print("== Report ========================================================")
    print("==================================================================")
    # Print report summary.
    #r.write_requests(s.finished)


    # only needed to test signal handler
    # signal.pause()


    # Dump hosts observed so far.   
    trace.report()


    # Dump registered components.
    #print()
    #for c in sim.components:
    #    print(c)


    sim.finalize()

    print()
    print("==================================================================")
    print("== Snapshot ======================================================")
    print("==================================================================")
    print(sim.persistency.path)

    print("\n>> Some commands to quickly inspect this run:")
    print("cd", sim.persistency.path)
    print("nautilus", sim.persistency.path)

    print()
    print("==================================================================")
    print("== Performance ===================================================")
    print("==================================================================")

    pass


if __name__ == '__main__':
    # Take the processing time.
    start = time.clock()
    main()
    end = time.clock()
    elapsed = end - start
    print('Process time:', elapsed, 'seconds')

