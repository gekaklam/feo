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


    Replacement Strategies:
        Least-recently used (LRU)



    """
    # TODO: link to simulation?


    def __init__(self, simulation=None, size=1000, speed=1000, replacement_strategy=None):
        super().__init__(simulation=simulation)

        # Cache configuration.
        self.size = size
        self.remain = size
        self.mode = None
        self.replacement_strategy = replacement_strategy

        # Cache State.
        self.fieldnames = ['size', 'accessed', 'modified', 'dirty']
        self.files = {} # cache is empty on startup

        # Register CSV report.
        self.report_name = 'cached_count'
        self.report_fieldnames = ['datetime', 'count', 'dirty']
        self.simulation.report.prepare_report(self.report_name, self.report_fieldnames)

        pass



    def replace(self, size):
        """ Replace enough files to accomodate size. """
        
        if self.replacement_strategy.lower() in ['lru', 'least recently used', 'least-recently used']:
           pass 

        else:
            self.log("ERROR: No replacement strategy set.")
            exit()
        



    def count_dirty(self):
        """ Return the number of dirty files. """

        count = 0
        files = self.files        

        for k, v in list(files.items()):
            if v['dirty'] == True:
                count += 1

        return count




    def clean_cache_by_age(self):
        """
        Clean up routines to keep the cache tidy.

        """
        
        files = self.files        

        for k, v in list(files.items()):
            #print("Check Expired:", files[k])
            if datetime.timedelta(0, 30, 0, minutes=0) < self.simulation.now() - v['modified']:
                #print("Expired:", files[k])
                del files[k]




    def clean_cache(self):
        """
        Clean up routines to keep the cache tidy.

        """
        
        files = self.files        

        for k, v in list(files.items()):
            #print("Check Expired:", files[k])
            if datetime.timedelta(0, 30, 0, minutes=0) < self.simulation.now() - v['modified']:
                #print("Expired:", files[k])
                del files[k]


    def lookup(self, name):
        """
        Checks if file exists

        """
        
        # use lookups also to clean up
        self.clean_cache()


        if name in self.files:
            return self.files[name]
        else:
            return False


    def set(self, name, tape=None, size=None, modified=None, dirty=None):
        """ Add or update a cache entry. """

        print("Cache set!")

        # create entry if not existent
        if not (name in self.files):
            dic = dict.fromkeys(self.fieldnames)
            self.files[name] = dic


        if size != None:
            self.files[name]['size'] = size
        else:
            self.error("Entry size not specified.")

        if modified != None:
            self.files[name]['modified'] = modified
        else:
            self.error("Entry modfied attribute not specified.")

        if dirty != None:
            self.files[name]['dirty'] = dirty
        else:
            self.error("Entry dirty flog not specified.")


        # stages changes, so log that for late analyis
        self.report_stages()


    def report_stages(self):
        """ Add the current stage count to the stages.csv with current model time. """
        dic = dict.fromkeys(self.report_fieldnames)

        dic['datetime'] = str(self.simulation.now())
        dic['count'] = str(len(self.files))

        self.simulation.report.add_report_row(self.report_name, dic)


    def dump(self):
        """Make snapshot of the file system state."""
        print("")
        self.simulation.log("Dump " + str(self) + " state.")
        for i, item in enumerate(self.files):
            self.simulation.log("%05d" % i + str(item) + str(self.files[item]))
        self.simulation.log(self.simulation.persistency.path)
        
