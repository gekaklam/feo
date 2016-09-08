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


class Cache(tapesim.components.Component.Component):
    """
    Caches in the model are more or less lookup tables that will forget entries
    after a certain time or when overflowing.


    Modes:
        Read-Through Caching
        Write-Through Caching
        Write-Behind Caching
        Refresh-Ahead Caching

        Read-Ahead


    """
    # TODO: link to simulation?

    size = None
    remain = None
    files = {} # cache is empty on startup

    def __init__(self, simulation=None, size=1000, speed=1000):
        super().__init__(simulation=simulation)

        self.size = size
        self.remain = size


        self.mode = None

        self.fieldnames = [
            'datetime',
            'count'
        ]
        self.simulation.report.prepare_report('stages', self.fieldnames)

        pass

    def clean_cache(self):
        """docstring for clean_cache"""
        
        files = self.files

        for k, v in list(files.items()):
            #print("Check Expired:", files[k])
            if datetime.timedelta(0, 30, 0, minutes=0) < self.simulation.now() - v['modified']:
                #print("Expired:", files[k])
                del files[k]

    def lookup(self, name):
        """Checks if file exists"""
        
        # use lookups also to clean up
        self.clean_cache()


        if name in self.files:
            return self.files[name]
        else:
            return False

    def set(self, name, tape=None, size=None, modified=None, persistent=None):
        # create entry if not existent
        if not (name in self.files):
            self.files[name] = {}
        
        if size != None:
            self.files[name]['size'] = size

        if modified != None:
            self.files[name]['modified'] = modified

        if persistent != None:
            self.files[name]['dirty'] = True

        # stages changes, so log that for late analyis
        self.report_stages()


    def report_stages(self):
        """ Add the current stage count to the stages.csv with current model time. """
        dic = dict.fromkeys(self.fieldnames)

        dic['datetime'] = str(self.simulation.now())
        dic['count'] = str(len(self.files))

        self.simulation.report.add_report_row('stages', dic)


