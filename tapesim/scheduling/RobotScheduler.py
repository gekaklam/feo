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


import math
import datetime


class Grid(object):
    

    def __init__(self, x, y):
        # dimensions in slots
        self.x = x
        self.y = y
        pass

    def tape_receive_time(self, tx, ty, rx, ry):
        a = math.fabs(rx - tx)
        b = math.fabs(ry - ty)
        return math.sqrt( math.pow(a,2) + math.pow(b,2) )



class RobotScheduler(object):

    # input for the scheduler is a graph
    def __init__(self, simulation=None):
        print("RobotScheduler instance.")

        self.simulation = simulation

        self.x = 0
        self.y = 0
        pass


    def receive_time(self, position):
        """Calculate the Receive-Time based on the Robot System"""
       
        tx = position[0]
        ty = position[1]

        g = Grid(3,4)

        rtime = datetime.timedelta(0, 5, 0) * g.tape_receive_time(tx, ty, self.x, self.y)
        return rtime

