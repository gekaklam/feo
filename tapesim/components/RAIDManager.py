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

    def __init__(self):
        print('FileManager instance.')
        
        self.files = {
                'abc': {'tape':'t1',  'size': 123, 'pos': 0},    
                'xyz': {'tape':'t1',  'size': 123, 'pos': 0},    
                'f1':  {'tape':'t1',  'size': 123, 'pos': 0},    
                'f2':  {'tape':'t10', 'size': 123, 'pos': 0},    
                'f3':  {'tape':'t20', 'size': 123, 'pos': 0},  
        }

        pass

    def lookup(self, name):
        """Checks if file exists"""
        if name in self.files:
            return self.files[name]
        else:
            return False

    def update(self, name, tape=None, size=None):
        # create entry if not existent
        if not (name in self.files):
            self.files[name] = {}
        
        # set fields idividually
        if tape != None:
            self.files[name][tape] = tape

        if size != None:
            self.files[name][size] = size

        return self.files[name]



