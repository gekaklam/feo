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


#{"gen": int, "thickness": "um", "lenght": "m", "tracks": int. "bit density": "bits/mm", "EEPROM": "kbit"}
ultrium_tape_specs = [
 {'gen': 1, 'thickness': 8.9, 'lenght': 609, 'tracks':  384, 'bit density':  4880, 'EEPROM':  32000},
 {'gen': 2, 'thickness': 8.9, 'lenght': 609, 'tracks':  512, 'bit density':  7398, 'EEPROM':  32000},
 {'gen': 3, 'thickness': 8.0, 'lenght': 680, 'tracks':  704, 'bit density':  9638, 'EEPROM':  32000},
 {'gen': 4, 'thickness': 6.6, 'lenght': 820, 'tracks':  896, 'bit density': 13250, 'EEPROM':  64000},
 {'gen': 5, 'thickness': 6.4, 'lenght': 846, 'tracks': 1280, 'bit density': 15142, 'EEPROM':  64000},
 {'gen': 6, 'thickness': 6.1, 'lenght': 846, 'tracks': 2176, 'bit density': 15143, 'EEPROM': 128000},
]

# Tape Geometry and other specs
# http://www.fujifilm.com/products/storage/lineup/ltoultrium/#specifications
ultrium_tape_dimensions = {'l': 102, 'w': 105.4, 'h': 21.5}
ultrium_tape_lifetime = 30 # years



class Tape(object):

    def __init__(self, *args, **kwargs):
        self.tid = None
        self.barcode = None

        self.capacity = None
        self.used = None
