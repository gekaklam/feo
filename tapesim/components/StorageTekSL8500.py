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

import tapesim.components.Component

class DriveGroup(object):
    """
    SL8500 has four 4x4 drive groups  => 16 * 4 => max. 64 drives
    """
    def __init__(self):
        self.drives = {}
        self.tapeman = None
        self.identity = None
        pass

    def install_drive(self, slot, drive):
        if slot in self.drives:
            msg = "Slot %s already contains a drive." % (slot)
            print("Error:", self.identiy, msg)
            exit(1)
        else:
            self.drives[slot] = drive


class StorageTekSL8500(tapesim.components.Component.Component):
    """
    StorageTek SL85000 Modular Library System is exabyte storage system with
    support for multiple generations of tape media.

    LTO Compatabile
    up to 8 partitions in a single library, or 16 in a library complexes
    

    capacity module!?  , adds 1728 slots

    64 drives

    1450 customer usable slots.. (that is not accounting for slots exclusive to system)


    14 slots high x ??
    demo shows: 13 slots high

    4 levels


    The library modules feature a number of components and allow for different
    customizations. The four core modules of a SL8500 are the following:

        * Customer Interface Module (CIM) (front)
            * Elevators (2 per CIM) (can move up to four cartridges)
        * Storage Expansion Module (SEM) (up to five SEMs)
        * Robotics Interface Module (RIM)
            * Pass-thru Ports (PTP) (allows to move up to 2 cartridges at a time)
        * Drive and Electronics Module (DEM)

    """

    def __init__(self, simulation, num_sems=5):
        super().__init__(simulation=simulation)

        self.levels = 4
        self.sems   = num_sems

        pass



    def get_nearest_slot(self, free=True, fill_level=None):
        return []
    
