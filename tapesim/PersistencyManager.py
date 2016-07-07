#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2016 Jakob Luettgau
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


import os
import sys
import datetime
import hashlib

class PersistencyManager(object):

    def __init__(self, path='./snapshots'):
        self.token_time = datetime.datetime.now()

        # generate fairly unique token
        h = hashlib.sha256()
        h.update(str(self.token_time).encode('utf-8'))
        h.update(os.uname()[1].encode('utf-8')) # hostname/nodename
        self.token_hash = h.hexdigest()

        self.snapshot = "%s_%s" % (
                self.token_time.isoformat(),
                self.token_hash[0:10]
            )
        self.path = "/".join([path, self.snapshot])

        # create directory structure
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            os.makedirs(self.path + "/visualizations")
            os.makedirs(self.path + "/requests")
            os.makedirs(self.path + "/reports")
            os.makedirs(self.path + "/library_state/")


     
        
        
