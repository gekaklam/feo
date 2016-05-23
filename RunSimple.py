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
import datetime
import time


# simulation and reporting facilities
import tapesim.Simulation as Simulation
import tapesim.Topology as Topology
import tapesim.Report as Report

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

    parser.add_argument('--config', type=int, help='')
    #parser.add_argument('--snapshot', help='')

    args = parser.parse_args()
    print(args)

    # Setup simulation
    print("")
    print("== Init Simulation ==")
    s = Simulation.Simulation()

    # Register Components and connect
    print("")
    print("== Prepare Topology ==")
    # load a topology from xml
    #t = Topology.Topology(s, network_xml='configs/network.xml') 
    t = Topology.Topology(s, network_xml='configs/network_IOServers.xml') 
    s.topology = t

#    client1 = Client.Client(s)
#
#    switch1 = Switch.Switch(s)
#    switch2 = Switch.Switch(s) # internal switch
#
#    io1 = IOServer.IOServer(s,has_cache=False)
#    cache_global = Cache.Cache(s)
#
#    drive1 = Drive.Drive(s)
#
#    library = Library.Library(s, 3, 4)
   



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
    Request.Request(s, s.clients[0], occur=tsu(10), attr={'file': 'abc', 'type': 'read', 'size': 100})
    Request.Request(s, s.clients[0], occur=tss(20), attr={'file': 'xyz', 'type': 'write', 'size': 100})


    # saturated network, correct update?
    Request.Request(s, s.clients[0], occur=tsu(10), attr={'file': 'abc', 'type': 'read', 'size': 10000})
    Request.Request(s, s.clients[0], occur=tsu(20), attr={'file': 'xyz', 'type': 'write', 'size': 10000})
    Request.Request(s, s.clients[0], occur=tsu(30), attr={'file': 'xyz', 'type': 'write', 'size': 200})
    Request.Request(s, s.clients[1], occur=tsu(40), attr={'file': 'xyz', 'type': 'write', 'size': 200})
    Request.Request(s, s.clients[0], occur=tsu(50), attr={'file': 'xyz', 'type': 'write', 'size': 200})

    Request.Request(s, s.clients[1], occur=tsu(100), attr={'file': 'xyz', 'type': 'read', 'size': 100})
    Request.Request(s, s.clients[1], occur=tsu(200), attr={'file': 'xyz', 'type': 'write', 'size': 200})
    Request.Request(s, s.clients[0], occur=tsu(300), attr={'file': 'xyz', 'type': 'read', 'size': 100})

    Request.Request(s, s.clients[0], occur=tsu(1000), attr={'file': 'abc', 'type': 'write', 'size': 100})
    Request.Request(s, s.clients[1], occur=tsu(2000), attr={'file': 'xyz', 'type': 'read', 'size': 250})
    Request.Request(s, s.clients[2], occur=tsu(3000), attr={'file': 'xyz', 'type': 'write', 'size': 600})

    Request.Request(s, s.clients[3], occur=tsu(10000), attr={'file': 'xyz', 'type': 'read', 'size': 100})
    Request.Request(s, s.clients[2], occur=tsu(20000), attr={'file': 'huh', 'type': 'read', 'size': 100})
    Request.Request(s, s.clients[0], occur=tsu(30000), attr={'file': 'xyz', 'type': 'read', 'size': 800})


    # start the simulation
    print()
    print("== Start Simulation ===============================================")
    s.start()

    # only needed to test signal handler
    # signal.pause()
   

    # dump registered components
    print()
    for c in s.components:
        print(c)

    pass


if __name__ == '__main__':
    # take the processing time
    start = time.clock()
    main()
    end = time.clock()
    elapsed = end - start
    print('\nProcess time:', elapsed, 'seconds')

