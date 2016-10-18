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


class FileManager(object):
    """Manages the files that exist in the system."""

    def __init__(self, simulation=None):

        print('FileManager instance.')
        
        self.simulation = simulation

        self.files = {}

        pass

    def lookup(self, name):
        """Checks if file exists"""
        if name in self.files:
            return self.files[name]
        else:
            return False


    def scan(self, entry):
        """Scan the data structure for a entry"""
        pass



    def update(self, name, tape=None, size=None, pos=0):
        # create entry if not existent
        if not (name in self.files):
            self.files[name] = {}
        
        # set fields idividually
        if tape != None:
            self.files[name]['tape'] = tape

        if size != None:
            self.files[name]['size'] = size

        self.files[name]['pos'] = pos

        return self.files[name]





    def dump(self):
        """Make snapshot of the file system state."""
        print("")
        self.simulation.log("Dump " + str(self) + " state.")
        for i, item in enumerate(self.files):
            self.simulation.log("%05d" % i, str(item), str(self.files[item]))
        self.simulation.log(self.simulation.persistency.path)
        

