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
import json
import random
locale.setlocale(locale.LC_ALL, 'en_US.utf8')


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

handling_signal = False
sim = None

def signal_handler(signal, frame):
    global handling_signal
    global sim

    try:
        print("\n Print handling signal?", handling_signal)
    except:
        pass

    if handling_signal:
        os._exit(0)

    handling_signal = True

    try:
        sim.topology.draw_graph('capacity', 'visualisation/waiting-for-user-confirmaiton-via-signal.pdf')
        print("\n What do you want to do?")
        handling_signal = True
        user = input("[Enter] to continue     OR      [Ctrl] + [C] to kill")
        handling_signal = True
    except:
        # do nothing, just to cope with print not being safe in signal handlers
        pass

    # reset, just in case user interaction failed
    handling_signal = False

    return




# register interrupt handler
signal.signal(signal.SIGINT, signal_handler)


def main():
    print()
    print("== Configuration ==")
    # maybe some environment variables?
    # print(os.environ['TAPESIM_'])

    global sim

    random.seed(42)



    parser = argparse.ArgumentParser(
        description='Simulating Tape Storage Libraries/Silos using the CRQ kernel. Chained Request Queues uses dedicated queues for Waiting Request, Disk I/O, Dirty Files, Tape I/O and Robots as well as IN and OUT going network traffic.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )




    parser.add_argument('tracefile', nargs='?', type=argparse.FileType('r'), default="../data/traces/dummy.xferlog")

    parser.add_argument('--network-topology', default="../data/topologies/dummy-network.xml")
    parser.add_argument('--library-topology', default="../data/topologies/dummy-library.xml")
    parser.add_argument('--drive-list', default="../data/other/drives.py-eval")


    parser.add_argument('--limit', type=int, help='', default=None)
    parser.add_argument('--limit-iterations', type=int, help='', default=-1)

    parser.add_argument('--config', type=int, help='')
    #parser.add_argument('--snapshot', help='')


    parser.add_argument("--confirm-step", help="Manually step through the simulation.", action="store_true")


    parser.add_argument("--debug", help="Be verbose.", action="store_true", default=False)
    parser.add_argument("--silent", help="Be not verbose.", action="store_true", default=False)



    parser.add_argument('--config-from-snapshot', help="Use the same configuration as path/to/snapshot.", default=None)


    args = parser.parse_args()
    print(args)


    print("PID:", os.getpid())
    user = input("Continue? [Enter]")


    print()
    print("==================================================================")
    print("== Initialize Simulation =========================================")
    print("==================================================================")
    sim = Simulation.Simulation(limit_iterations=args.limit_iterations, confirm_step=args.confirm_step, debug=args.debug)


    ###########################################################################
    # Register Components and connect
    ###########################################################################
    print()
    print("==================================================================")
    print("== Prepare Topology ==============================================")
    print("==================================================================")
    # load a topology from xml
    #t = Topology.Topology(s, network_xml='configs/network.xml')
    t = Topology.Topology(sim, network_xml=args.network_topology)
    sim.topology = t

    # Set provider limit (how many requests to process).
    limit = None
    if args.limit:
        limit = args.limit


    print()
    print("==================================================================")
    print("== Prepare File and Tape System ==================================")
    print("==================================================================")

    # Rebuild tape filesystem:
    print()
    mkfs = RebuildFilesystem.RebuildFilesystem(sim, args.tracefile, limit=None, debug=args.debug)
    # Disable debug for tape manager during rebuild filesystem to speed up.
    sim.tm.debug = False
    mkfs.rebuild_filesystem()
    sim.tm.debug = True


    print()
    print("Files:", len(sim.fm.files))
    #for f in sim.fm.files:
    #    print(f, sim.fm.files[f])
    print("Tapes:", len(sim.tm.tapes))
    #pprint.pprint(sim.tm.tapes)

    # Open tracefile and register provider
    trace = ProviderXferlog.ProviderXferlog(sim, args.tracefile, limit=limit, client_link_capacity=15000)
    sim.provider.append(trace)



    print()
    print("==================================================================")
    print("== Install Drives ================================================")
    print("==================================================================")

    # Install a number of tape drives.
    drives_file = open(args.drive_list, 'r')
    drives_raw = drives_file.read()
    drives = eval(drives_raw)

    pprint.pprint(drives)

    for i,d  in enumerate(drives):
        #drivename = "%s Drive %d" % (d["type"], i)
        drivename = "%s" % (d["type"])
        link_capacity = Drive.drive_specs[d['type']]['throughput'][0]
        new_drive = sim.topology.register_network_component(
                name=drivename,
                link_capacity=link_capacity,
                drive=True
            )


    sim.topology.draw_graph('capacity', 'visualisation/after-installation.pdf')

    print("PID:", os.getpid())
    user = input("Continue? [Enter]")

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
