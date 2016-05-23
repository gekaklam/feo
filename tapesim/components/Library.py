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


import tapesim.components.Component
import math


class Library(tapesim.components.Component.Component):
    

    def __init__(self, simulation, x, y):
        super().__init__(simulation=simulation)

        # dimensions in slots
        self.x = x
        self.y = y
        
        pass

    def tape_receive_time(self, tx, ty, rx, ry):
        a = math.fabs(rx - tx)
        b = math.fabs(ry - ty)
        return math.sqrt( math.pow(a,2) + math.pow(b,2) )



