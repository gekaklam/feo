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

import random
import math



import tapesim.components.Component

class TapeManager(tapesim.components.Component.Component):



    def __init__(self, simulation):
        self.log("TapeManager instance.")

        self.simulation = simulation

        self.slots = {}

        self.tapes = {}
#       self.tapes = {
#            "t1": {"slot": (1, 1), "free": 500, "type": "u4"},    
#            "t2": {"slot": (1, 2), "free": 500, "type": "u4"},    
#            "t3": {"slot": (1, 3), "free": 500, "type": "u4"},    
#            "t4": {"slot": (2, 1), "free": 500, "type": "u4"},    
#            "t5": {"slot": (2, 2), "free": 500, "type": "u4"},    
#            "t6": {"slot": (2, 3), "free": 500, "type": "u4"},    
#            
#            "t10": {"slot": (1, 4), "free": 1000, "type": "u5"},    
#            "t20": {"slot": (1, 4), "free": 1000, "type": "u5"},    
#
#'01338': {'free': 6755399434266624, 'slot': (1, 9)},
# '03796': {'free': 6755399437901824, 'slot': (5, 11)},
# '04792': {'free': 6755388703637504, 'slot': (7, 9)},
# '05479': {'free': 6755399437901824, 'slot': (4, 10)},
# '08801': {'free': 6755397522919424, 'slot': (7, 9)},
# '09162': {'free': 6755399426883584, 'slot': (0, 8)},
# '09511': {'free': 6755396465967104, 'slot': (5, 11)},
# '13230': {'free': 6755399432198144, 'slot': (6, 12)},
# '14281': {'free': 6755398912528384, 'slot': (7, 4)},
# '14469': {'free': 6755399432198144, 'slot': (7, 6)},
# '15028': {'free': 6755398976251904, 'slot': (7, 8)},

# '15728': {'free': 6755398980972544, 'slot': (1, 2)},
# '15930': {'free': 6755399437901824, 'slot': (6, 3)},
# '16326': {'free': 6755399432198144, 'slot': (0, 5)},
# '17389': {'free': 6755399440001024, 'slot': (6, 4)},
# '18418': {'free': 6755397947592704, 'slot': (2, 6)},
# '19524': {'free': 6755399437901824, 'slot': (5, 12)},
# '20200': {'free': 6755399437901824, 'slot': (2, 2)},
# '20655': {'free': 6755393385150464, 'slot': (6, 4)},
# '21624': {'free': 6755399434266624, 'slot': (5, 0)},
# '22130': {'free': 6755398372276224, 'slot': (6, 10)},
# '22188': {'free': 6755399437901824, 'slot': (7, 12)},
# '23346': {'free': 6755398796949504, 'slot': (0, 0)},
# '23777': {'free': 6755399437901824, 'slot': (3, 2)},
# '24132': {'free': 6755399440001024, 'slot': (5, 2)},
# '25371': {'free': 6755397730535424, 'slot': (0, 0)},
# '30767': {'free': 6755399426412544, 'slot': (3, 7)},
# '34624': {'free': 6755399226343424, 'slot': (5, 0)},
# '36898': {'free': 6755398152863744, 'slot': (2, 1)},
# '37729': {'free': 6755398152863744, 'slot': (4, 12)},
# '37850': {'free': 6755399299293184, 'slot': (3, 2)},
# '38986': {'free': 6755396959842304, 'slot': (2, 11)},
# '40475': {'free': 6755399432198144, 'slot': (2, 5)},
# '41515': {'free': 6755399424528384, 'slot': (2, 3)},
# '42622': {'free': 6755398990413824, 'slot': (5, 2)},
# '43113': {'free': 6755399432198144, 'slot': (4, 4)},
# '46436': {'free': 6755399424518144, 'slot': (2, 13)},
# '47383': {'free': 6755399437901824, 'slot': (0, 9)},
# '47746': {'free': 6755398801670144, 'slot': (7, 11)},
# '50822': {'free': 6755396036552704, 'slot': (2, 2)},
# '50953': {'free': 6755399437901824, 'slot': (3, 12)},
# '51004': {'free': 6755399437901824, 'slot': (4, 9)},
# '55467': {'free': 6755399437901824, 'slot': (1, 0)},
# '57179': {'free': 6755399104415744, 'slot': (4, 9)},
# '57408': {'free': 6755398756839424, 'slot': (5, 4)},
# '62688': {'free': 6755397310582784, 'slot': (1, 6)},
# '65365': {'free': 6755394741315584, 'slot': (2, 6)},
# '66180': {'free': 6755399226343424, 'slot': (7, 9)},
# '67673': {'free': 6755398162305024, 'slot': (7, 7)},
# '69439': {'free': 6755397310582784, 'slot': (0, 1)}
#
#    }


        pass


    def lookup(self, name):
        """Checks if file exists"""
        if name in self.tapes:
            return self.tapes[name]
        else:
            return False


    def update(self, name, size=None):
        # create entry if not eistent
        if not (name in self.tapes):
            tapes[name] = {}
        
        # set fields idividually
        if size != None:
            tapes[name][size] = size

        return tapes[names]


    def allocate(self, size, compression=False, raid=None):
        """Allocate tape storage of size."""

        # TODO: wild allocation policies here
        # => priority queue?
        # how do you account for locality?
    
        result = False

        tid = "%05d" % random.randint(1, 50000)


        if tid in self.tapes:
            # present check fill
            self.log("check fill level")
            result = self.tapes[tid]
        else:
            # new tape
            self.log("NEW TAPE:")
            
            self.log("NEW SLOT:")
            tries = 10
            slot_lim = 300
            slotid = (random.randint(0, slot_lim), random.randint(0, slot_lim))
            while slotid in self.slots and tries > 0:
                tries -= 1
                self.log("SLOT TAKEN:", slotid)
                slotid = (random.randint(0, slot_lim), random.randint(0, slot_lim))

            if slotid in self.slots:
                self.error("Tape library overfull. No free slots.")

            self.slots[slotid] = {'tape': tid}

            self.log('slot:', slotid)

            self.tapes[tid] = {'free': int(math.pow(1024, 4) * 6), 'slot': slotid}
            result = self.tapes[tid]



        # naive
        #for tape in self.tapes:
        #    if tape["free"] >= size:
        #        # we found a suitable tape
        #        result = tape
        #        break

        return tid, result


    def dump(self):
        """Make snapshot of the file system state."""
        print("")
        self.simulation.log("Dump " + str(self) + " state.")
        for i, item in enumerate(self.tapes):
            self.simulation.log("%05d" % i + str(item) + str(self.tapes[item]))
        self.simulation.log(self.simulation.persistency.path)



