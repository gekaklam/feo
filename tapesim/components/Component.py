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
import sys
import traceback

import graph_tool.all as gt


class Component(object):
    """
    Components, as in hardware or software components which are required to
    handle a request to a clients satisfaction.

    A components in general is considered a resource that in principle is
    limited. Therefor methods for allocation and release of capacity are
    exposed for every object inheriting Component.


    """


    def __init__(self, simulation=None, name=None):
        self.simulation = simulation     # e.g. to receive model time
        self.active_requests = []
        self.is_aborting = False
        self.next_event = None

        if simulation != None:
            self.simulation.components.append(self)

        self.name = name

        # Especially hardware components are relatively tightly coupled with
        # the topologies which is currently implemented using graphs.
        self.graph = None
        self.nodeidx = None

        # 
        self.capacity = 1
        self.max_capacity = 1

        pass

   
    def free_capacity(self, size=1):
        print("FREE", self.__repr__())

        if (self.capacity + size) <= self.max_capacity:
            self.capacity += size
        else:
            print("Error: trying to free capacity that was never there!")


    def allocate_capacity(self, size=1):
        """docstring for block"""
        print("ALLOC", self.__repr__())

        if self.capacity >= size:
            self.capacity -= size
            return size
        else:
            print("Warning: Could not allocate!", self.__repr__())
            return False


    def has_capacity(self, size=1):
        """Poll the component for activity"""
        if self.capacity >= size:
            return True
        else:
            return False


    def ready(self):
        """Easy interface to poll if the component is ready."""
        if self.busy_until <= self.simulation.now():
            return True
        else:
            return False
    

    def abort(self):
        """Initiate abort of current task. The default behaviour checks if the
        component is already aborting and sets busy_until for the the time
        required to get into ready state."""

        # become ready immedietly
        if not is_aborting:
            self.busy_until = self.simulation.now()


    def __repr__(self):
        info = 'nodeidx=%s' % (str(self.nodeidx))
        info += " "
        if self.graph != None:
            info += self.graph.vp.name[self.nodeidx]

        if self.name != None:
            info += self.name

        adr = hex(id(self))
        return '<%s %s: %s>' % (adr, self.__class__.__name__, info)



    def log(self, *args, level=0, tags=[], **kargs):                                                    
        print("[%s]" % self.__class__.__name__, *args, **kargs)


    def error(self, *args, level=0, tags=[], **kargs):                                                    
        # Print a stack trace.
        for line in traceback.format_stack():
            print(line.strip())

        # Exit with error description.
        print("[%s] ERROR:" % self.__class__.__name__, *args, **kargs)
        exit(1)

