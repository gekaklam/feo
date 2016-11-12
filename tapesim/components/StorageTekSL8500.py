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
import csv
import re
import math

import pprint

import tapesim.components.Component
import tapesim.components.Drive as Drive



def travel_time_easing(distance, max_velocity, accelleration, decceleration=None):
    """ 
        distance        m
        max_velocity    m/s
        accelleration   m/s/s
        decelleration   m/s/s

        trapezoid equation to account for accelleration

           +-----------------+
          /|                 |\
         / |                 | \
        +--+-----------------+--+

         accelleration phase
        <-->                 <-->
                              decceleration phase

        <----------------------->
           total distance/time

    """
    if decceleration is None:
        decceleration = accelleration

    # TODO, seperate decelleration time

    time_max = (distance - distace_acc - distance_decc) / max_velocity

    total_time = time_acc + time_dec + time_max


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


class Complex(tapesim.components.Component.Component):
    """
    SL8500 Library Complex

    Notes:
    Actually, I do not like the idea to define a Complex class for every type of library.
    """

    def __init__(self):

        pass






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

        self.rails = 4
        self.drive_cols = 2
        self.drive_cols_total = self.drive_cols * 2

      
        self.column_mask = ['D','D', 'PTP', 'SEM', 'SEM', 'SEM', 'SEM', 'SEM', 'ELEVATOR']
        self.slot_mask = [1,0,2,3,4,5,6,7,8,9,10,11,12,0,13]


        self.elevator_column = 0

        self.honor_dead_rows = True


        # SL8500 systems are purchased
        self.num_sems   = num_sems

            
        # Map of installed drives.
        self.drives = {}


        # calculate number of useable slots
        num_slots_outer = 13 * 4 * 2 * (3 + self.num_sems * 8 + 2 + 3) 
        num_slots_inner = 13 * 4 * 2 * (3 + self.num_sems * 8 + 2)
        self.num_slots = num_slots_inner + num_slots_outer

        pass




    def install_drives(self, csv_filepath, register_to_network_topology=True):
        """ Initialize library unit with the drive configuration as provided.

        """
        fieldnames = [
            'pos_firmware',
            'unknown-1',
            'pos_hpss',
            'bay',
            'status_network',
            'status_drive',
            'drive_type',
            'unknown-2',
            'unknown-4',
            'mac',
            'unknown-5',
            'link_type',
            'unknown-6',
            'unknown-7',
            'complex'
        ]

        csvfile = open(csv_filepath, 'r')
        reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter='\t')



        # regex to find drive bay
        #bay_hpss = 

        for row in reader:
            if row['pos_firmware'] == '' and row['pos_hpss'] == '':
                continue

       
            # complex, rail, column, ?, 'bay'
            #pos_firmware = re.findall(r'', row['pos_firmware'])
            pos_firmware = row['pos_firmware'].split(',')
            pos_firmware = (pos_firmware[0], pos_firmware[1], pos_firmware[2], pos_firmware[3], pos_firmware[4])
            pos_firmware = tuple(map(int, pos_firmware))
            print(pos_firmware)


            new_drive = Drive.Drive(self.simulation, type=row['drive_type'], library_pos=pos_firmware)

            self.drives[pos_firmware] = new_drive
            print(row)


        pprint.pprint(self.drives)



    def get_cm_coordinates(self, library_component):

        # drives
        dw = 10.0
        dh = 4.0 * 3
        dxsep = 4.0
        dysep = 4.0

        # slots
        sw = 10.0
        sh = 4.0
        sxsep = 0.0
        sysep = 0.0

        semxsep = 5.0

        # elevator
        ew = 10.0
        eh = 4.0 * 13
        exsep = 0.0
        eysep = 0.0

        # y offsets do not happen currently
        dxoff = dxsep/2.0 + 2.0 * (dw + dxsep)
        sxoff = 20.0 * (sw + sxsep)
        exoff = 0.0

        if library_component.__class__.__name__ in ['Slot', 'tuple']:
            # default, tuple to slot
            print("cm_coordinates for slots")

            #pos = (library, rail, column, inner/outer, slot)
       

            pos = library_component

            xpos = pos[2]
            ypos = pos[4]

            xsign = 1.0
            if xpos < 0:
                xsign = -1.0

            ysign = 1.0
            if ypos < 0:
                ysign = -1.0

            xpos = math.fabs(pos[2]) - self.drive_cols
            ypos = math.fabs(pos[4])

            dead_rows = 0
            if ypos > 1 and self.honor_dead_rows == True:
                dead_rows += 1

            if ypos > 11 and self.honor_dead_rows == True:
                dead_rows += 1

            print("dead_rows = %d" % dead_rows)

            ypos += dead_rows


            #x = dxoff + (xpos - 1) * (sw + sxsep) + sw/2.0
            x = (xpos - 1) * (sw + sxsep) + sw/2.0
            y = (ypos - 1) * (sh + sysep) + sh/2.0

            return (xsign * x, ysign * y)



        elif library_component.__class__.__name__ in ['Drive']:
            print("cm_coordinates for drives", library_component)

            #pos = (library, rail, column, inner/outer, slot)
            pos = library_component.library_pos
            
            xpos = pos[2]
            ypos = pos[4]

            xsign = 1.0
            if xpos < 0:
                xsign = -1.0

            ysign = 1.0
            if ypos < 0:
                ysign = -1.0

            xpos = math.fabs(pos[2])
            ypos = math.fabs(pos[4])

            
            xsep = 4.0
            ysep = 4.0

            x = dxsep/2.0 + (xpos - 1) * (dw + dxsep) + dw/2.0
            y = (ypos - 1) * (dh + dysep) + dh/2.0

            return (xsign * x, ysign * y)



        elif library_component.__class__.__name__ in ['Elevator']:
            print("cm_coordinates for elevator")

            pass


        elif library_component.__class__.__name__ in ['PassThroughPort']:
            print("cm_coordinates for pass-through-port")

            pass
        


    def get_logical_coordinates(self, cm_coordinates):
        pass




    def get_nearest_slot(self, free=True, fill_level=None):
        return []
  



