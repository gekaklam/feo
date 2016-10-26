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

import pprint

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


    def __init__(self, simulation=None, size=1000, speed=100000, replacement_strategy=None, replace_sim_fc=False):
        super().__init__(simulation=simulation)

        # Cache configuration.

        capacity = size # TODO: change in constructur and components currently using it differently

        self.capacity = capacity
        self.max_capacity = capacity

        self.mode = None
        self.replacement_strategy = replacement_strategy

        # Cache State.
        self.fieldnames = ['size', 'accessed', 'modified', 'dirty', 'name']
        self.files = {} # cache is empty on startup

        # Register CSV report.
        self.report_name = 'cached_count'
        self.report_fieldnames = ['datetime', 'count', 'dirty']
        self.simulation.report.prepare_report(self.report_name, self.report_fieldnames)


        if replace_sim_fc == True:
            print("INFO: Replaced default file cache!")
            self.simulation.fc = self

        pass



    def replace(self, size=None, name=None):
        """ Replace enough files to accomodate size. """
      
        if size == None and name == None:
            self.error("You have to specify at least one: Size or name to be replace.")


        # least recently used
        LRU = list(self.files)
        pprint.pprint(LRU)
        LRU.sort(key=lambda x: self.files[x]['modified'])
        pprint.pprint(LRU)

        while self.capacity < size:
            filename = LRU.pop(0) 
            print(filename)
            self.free_capacity(self.files[filename]['size'])
            self.files.pop(filename, None)

        return


        # TODO:
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
        #self.clean_cache()


        if name in self.files:
            return self.files[name]
        else:
            return False


    def allocate_capacity(self, size=1):
        """docstring for block"""
        print("ALLOC", self.__repr__())

        if size >= self.max_capacity:
            self.error("Tried to allocate larger than max capacity.", self.__repr__())
        
        # check if we need to replace any elements
        if size > self.capacity:
            # we have to free some space
            self.replace(size - self.capacity)

        if self.capacity >= size:
            self.capacity -= size
            return size
        else:
            self.error("Warning: Could not allocate!", self.__repr__())
            return False


    def set(self, name, tape=None, size=None, modified=None, dirty=None):
        """ Add or update a cache entry. """

        print("Cache set!")

        # create entry if not existent
        if not (name in self.files):
            self.allocate_capacity(size=size)
            dic = dict.fromkeys(self.fieldnames)
            self.files[name] = dic


        self.files[name]['name'] = name


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
        
