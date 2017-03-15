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


import time
import argparse
import sys
import os
import re
import datetime
import random
import pprint
import traceback




class XferlogSanitizer(object):
    """ Read a complete
    """


    def __init__(self, tracefile, limit=None, debug=None):

        # Configuration
        self.limit = limit
        self.tracefile = tracefile

        # Statistics
        self.requests = []
        self.requests_dropped = []

        self.clients = {}
        self.files = {}

        self.lines = 0
        self.reads = 0
        self.writes = 0
        self.other = 0

        self.size_min = 0
        self.size_max = 0
        self.sizes = []

        self.last_timestamp = None

        # Enable/disable debug output
        self.debug = None
        if debug != None:
            self.debug = debug



    def sanitize_type(self, typestring):
        WRITE = ['PSTO_Cmd', 'STOR_Cmd']
        READ = ['PRTR_Cmd', 'RETR_Cmd']

        if typestring in READ:
            return 'read'
        elif typestring in WRITE:
            # TODO: REVERT!
            #return 'write'
            return 'read'
        else:
            return 'unknown:%s' % typestring


    def read(self):
        """Read trace file into memory."""

        self.log("Reading file (this may take a while).", force=True)
        # Take time for this operation.
        start = time.clock()

        result = (True, None)
        while result is not None:
            result = self.fetch_one()

            if result is None:
                break;

            if result[0] is True:
                self.requests.append(result[1])
            elif result[0] is False:
                self.log(result[1], force=True)
                self.requests_dropped.append(result[1])

            self.log(len(self.requests))
            self.log()



        end = time.clock()
        elapsed = end - start
        self.log('Process time (read):', elapsed, 'seconds', force=True)

    def sort(self):
        self.log("TODO sort")
        start = time.clock()

        # Sort.
        self.requests.sort(key=lambda item: item['timestamp'], reverse=False)

        end = time.clock()
        elapsed = end - start
        self.log('Process time (sort):', elapsed, 'seconds', force=True)

    def write(self, outfile, anonymize=False):

        DATE_FORMAT = "%a %b %-d %H:%M:%S %Y"

        for request in self.requests:
            print(request)

            # Template to parse xferlog entry:
            # 0   1   2   3      4    5           6                               7        8
            # wd  mon day time   year client      file                            type     bytes
            # Tue Dec 1 00:01:11 2015 10.50.35.16 2100_ten/2084/208404_qtimer.tar PSTO_Cmd 14643200

            if anonymize is True:
                line = " ".join([
                    request['timestamp'].strftime(DATE_FORMAT),
                    self.clients[request['client']],
                    self.files[request['filename']],
                    request['type'],
                    str(request['size'])
                ])
            else:
                line = " ".join([
                    request['timestamp'].strftime(DATE_FORMAT),
                    request['client'],
                    request['filename'],
                    request['type'],
                    str(request['size'])
                ])



            outfile.write(line + '\n')

        return

    def check(self, tracefile):

        self.last_timestamp = timestamp
        # guard against unsorted xferlog
        # if self.last_timestamp != None and timestamp < self.last_timestamp:
        #    print("vim %s:%d" % (self.tracefile.name, self.counter))
        #    self.error("Date in trace not monoton increasing.", self.counter, raw_req)
        pass


    def fetch_one(self):
        """Fetch one event from trace and try to parse it."""

        status = True

        # Template to parse xferlog entry:
        # 0   1   2   3      4    5           6                               7        8
        # wd  mon day time   year client        file                            type     bytes
        # Tue Dec 1 00:01:11 2015 10.50.35.16 2100_ten/2084/208404_qtimer.tar PSTO_Cmd 14643200
        DATE_FORMAT = "%b %d %H:%M:%S %Y"  # what about %a?

        # Check EOT.
        line = self.tracefile.readline()
        if line == '' or (self.limit != None and self.counter >= self.limit):
            self.log("END OF TRACE")
            return None

        # Keep track of events provided.
        self.lines += 1

        # Parse raw event string.
        raw_req = line.split(' ')
        date_string = "%s %02d %s %s" % (raw_req[1], int(raw_req[2]), raw_req[3], raw_req[4])

        # Datetime
        timestamp = None
        timestamp = datetime.datetime.strptime(date_string, DATE_FORMAT)

        # Client
        client = None
        client = raw_req[5]
        if client not in self.clients.keys():
            self.log("Client not present.")
            self.clients[client] = "%s%s" % ("client", len(self.clients))

        # Filename
        filename = None
        filename = raw_req[6]
        if filename not in self.files.keys():
            self.log("File not present.")
            self.files[filename] = "%s%s" % ("file", len(self.files))

        # Size
        size = None
        try:
            size = int(raw_req[8])
        except ValueError:
            self.log("Could not parse size.", force=True)
            status = False

        # Type
        type = None
        type = raw_req[7]



        self.log(self.clients[client])
        self.log(self.files[filename])

        #request = {'raw': line, 'filename': filename, 'type': type, 'size': size, 'client': client, 'timestamp': timestamp}
        request = {'filename': filename, 'type': type, 'size': size, 'client': client, 'timestamp': timestamp}

        self.log(request)

        return (status, request)

    def report(self):
        print("Lines:    ", self.lines)
        print("Requests: ", len(self.requests))
        print("Dropped:  ", len(self.requests_dropped))
        print("Reads:    ", self.reads)
        print("Writes:   ", self.writes)
        print("Other:    ", self.other)
        print("Total:    ", self.reads + self.writes + self.other)
        print("Clients:  ", len(self.clients))
        print("Files:    ", len(self.files))

        print()
        print("Size(min):", self.size_min)
        print("Size(max):", self.size_max)

    def log(self, *args, level=0, tags=[], force=False, **kargs):
        # exit early? debug off?
        if self.debug == False and force == False:
            return

        # print("[%s] " % self.__class__.__name__, *args, **kargs)
        print(*args, **kargs)

    def error(self, *args, level=0, tags=[], **kargs):
        # Print a stack trace.
        for line in traceback.format_stack():
            print(line.strip())

        # Exit with error description.
        print("[%s] ERROR:" % self.__class__.__name__, *args, **kargs)
        exit(1)


def main():
    print()
    print("== Configuration ==")
    # maybe some environment variables?
    # print(os.environ['TAPESIM_'])

    parser = argparse.ArgumentParser(
        description='Sanitizes (sort, remove invalid) and optionally anonymizes xferlog file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

    parser.add_argument('-i', '--infile', nargs='?', type=argparse.FileType('r'), default="in.xferlog", help='input file')
    parser.add_argument('-o', '--outfile', nargs='?', type=argparse.FileType('w'), default="out.xferlog", help='output file')
    parser.add_argument('-n', '--limit', type=int, help='', default=None)
    parser.add_argument('--anonymize', help='anonymize file and host names', action='store_true', default=False)
    parser.add_argument('--debug', help='', action='store_true', default=False)

    args = parser.parse_args()
    print(args)

    sanitizer = XferlogSanitizer(tracefile=args.infile, debug=args.debug)
    sanitizer.read()
    sanitizer.sort()
    sanitizer.write(args.outfile, anonymize=args.anonymize)

    sanitizer.report()


if __name__ == '__main__':
    # Take the processing time.
    start = time.clock()
    main()
    end = time.clock()
    elapsed = end - start
    print('Process time:', elapsed, 'seconds')
