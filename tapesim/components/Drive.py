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
import re


import tapesim.components.Component


#{"gen": int, "thickness": "um", "lenght": "m", "tracks": int. "bit density": "bits/mm", "EEPROM": "kbit"}
tape_specs = {
        'LTO-1': {'gen': 1, 'thickness': 8.9, 'lenght': 609, 'tracks':  384, 'bit density':  4880, 'EEPROM':  32000},
        'LTO-2': {'gen': 2, 'thickness': 8.9, 'lenght': 609, 'tracks':  512, 'bit density':  7398, 'EEPROM':  32000},
        'LTO-3': {'gen': 3, 'thickness': 8.0, 'lenght': 680, 'tracks':  704, 'bit density':  9638, 'EEPROM':  32000},
        'LTO-4': {'gen': 4, 'thickness': 6.6, 'lenght': 820, 'tracks':  896, 'bit density': 13250, 'EEPROM':  64000},
        'LTO-5': {'gen': 5, 'thickness': 6.4, 'lenght': 846, 'tracks': 1280, 'bit density': 15142, 'EEPROM':  64000},
        'LTO-6': {'gen': 6, 'thickness': 6.1, 'lenght': 846, 'tracks': 2176, 'bit density': 15143, 'EEPROM': 128000},

        # IBM
        'T9840A':  {'gen': None, 'thickness': 6.1, 'lenght': 846, 'tracks': 288, 'bit density': 15143, 'EEPROM': 128000},
        'T9840B':  {'gen': None, 'thickness': 6.1, 'lenght': 846, 'tracks': 288, 'bit density': 15143, 'EEPROM': 128000},
        'T9840C':  {'gen': None, 'thickness': 6.1, 'lenght': 846, 'tracks': 288, 'bit density': 15143, 'EEPROM': 128000},

        'T10000':  {'gen': None, 'thickness': 6.1, 'lenght': 917, 'tracks': 2176, 'bit density': 15143, 'EEPROM': 128000, 'capacity': "500GB"},

}


#{"gen": 1, "capacity": GB: (plain, compressed), "throughput" MB/s: (plain, compressed), "read_compatible": [], "write_compatible": [], "since": "year"},
drive_specs = {
        # LTO / Ultrium
        'LTO-1':  {'gen':  1, 'capacity': (  100,   200), 'throughput': (  20,  40), 'compatible': {'w': [1],    'r': [1]},      'since': 2000},
        'LTO-2':  {'gen':  2, 'capacity': (  200,   400), 'throughput': (  40,  80), 'compatible': {'w': [1,2],  'r': [1,2]},    'since': 2002},
        'LTO-3':  {'gen':  3, 'capacity': (  400,   800), 'throughput': (  80, 160), 'compatible': {'w': [2,3],  'r': [1,2,3]},  'since': 2004},
        'LTO-4':  {'gen':  4, 'capacity': (  800,  1600), 'throughput': ( 120, 240), 'compatible': {'w': [3,4],  'r': [2,3,4]},  'since': 2007},
        'LTO-5':  {'gen':  5, 'capacity': ( 1500,  3000), 'throughput': ( 140, 280), 'compatible': {'w': [4,5],  'r': [3,4,5]},  'since': 2010},
        'LTO-6':  {'gen':  6, 'capacity': ( 2500,  6250), 'throughput': ( 160, 400), 'compatible': {'w': [5,6],  'r': [4,5,6]},  'since': 2012},
        'LTO-7':  {'gen':  7, 'capacity': ( 6000, 15000), 'throughput': ( 300, 750), 'compatible': {'w': [6,7],  'r': [5,6,7]},  'since': 2015},
        'LTO-8':  {'gen':  8, 'capacity': (12800, 32000), 'throughput': ( 472,1180), 'compatible': {'w': [7,8],  'r': [6,7,8]},  'since': None},
        'LTO-9':  {'gen':  9, 'capacity': (25000, 62500), 'throughput': ( 708,1770), 'compatible': {'w': [8,9],  'r': [7,8,9]},  'since': None},
        'LTO-10': {'gen': 10, 'capacity': (48000,120000), 'throughput': (1100,2750), 'compatible': {'w': [9,10], 'r': [8,9,10]}, 'since': None},

        # IBM
        'T9840A': {'gen': None, 'capacity': (20,20), 'throughput': (1100,2750), 'compatible': {'w': [], 'r': []}, 'since': None, 'rewind_speed': '11.0m/s'},
        'T9840B': {'gen': None, 'capacity': (20,20), 'throughput': (1100,2750), 'compatible': {'w': [], 'r': []}, 'since': None, 'rewind_speed': '11.0m/s'},
        'T9840C': {'gen': None, 'capacity': (20,20), 'throughput': (1100,2750), 'compatible': {'w': [], 'r': []}, 'since': None, 'rewind_speed': '11.0m/s'},

        'T9940': {'gen': None, 'capacity': (20,20), 'throughput': (1100,2750), 'compatible': {'w': [], 'r': []}, 'since': None},

        'T10000a': {'gen': None, 'capacity': (48000,120000), 'throughput': (1100,2750), 'compatible': {'w': [], 'r': []}, 'since': None},
        'T10000b': {'gen': None, 'capacity': (2000,120000), 'throughput': (1100,2750), 'compatible': {'w': [], 'r': []}, 'since': None},
}

class Drive(tapesim.components.Component.Component):
    """
    The generic drive class used meet the API requirements of the Simulator.
    Since LTO (Linear Tape Open) is an important industry standard supported by
    varius vendors it is the default choice when instantiating drives and
    tapes.
    """

    def __init__(self, simulation, type=None, lto_generation=None, specs=None, verbose=False, library_pos=None):
        super().__init__(simulation=simulation)
        self.simulation.drives.append(self)

        # available fields
        self.throughput = 0


        # When type string is provided try to set specs according to known drive types.
        if type != None:
            type = self.sanitize_type(type)


        self.type = type

        if specs != None:
            self.specs = specs
            self.throughput = specs['throughput']
        elif lto_generation != None:
            self.throughput = drive_specs[lto_generation]['throughput'][0]


        self.library_pos = library_pos


        pass




    def sanitize_type(self, type):
        """ Fix some common and known aliases to match the list of known drives. """

        # LTO drive?
        result = re.findall(r'Ultrium([0-9]+)', type)
        print(result)

        if len(result):
            type = "LTO-" + result[0][0]
            return type



        return type





    def get_spool_time(self, pos=None, tape=None, filename=None):
        """
        Return timedelta for spool time for certain position or file.
        """
        # TODO:
        # I am not sure if the info stored on the EEPROM is also available
        # in the disk database and therefor available for consideration by
        # the scheduler.

        #if pos != None:
        #    stime = datetime.timedelta(0, 0, 333) * pos

        #elif tape != None and filename != None:
        #    # TODO
        #    pass

        #else:
        #    stime = datetime.timedelta(0, 1, 0) * 3
        #    pass

        # or simply assume 30 seconds?
        stime = datetime.timedelta(0, 1, 0) * 30

        return stime





    def __repr__(self):
        info = 'nodeidx=%s' % (str(self.nodeidx))
        info += " "
        if self.graph != None:
            info += self.graph.vp.name[self.nodeidx]

        if self.name != None:
            info += self.name


        if self.library_pos != None:
            info += "lib_pos=%s" % str(self.library_pos)

        if self.type != None:
            info += "type=%s" % self.type


        adr = hex(id(self))
        return '<%s %s: %s>' % (adr, self.__class__.__name__, info)
