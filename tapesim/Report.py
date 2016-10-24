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

import csv
import sqlite3
import os
import pprint

class Report(object):

    def __init__(self, simulation=None, filepath="./"):

        # use simulation persistency settings
        self.simulation = simulation

        if self.simulation == None:
            self.filepath = filepath
        else:
            self.filepath = self.simulation.persistency.path


        self.reports = {        
        }


        self.fieldnames = [
            'occur',
            'finish',
            'type',
            'megabytes',
            'wait_time_tape',
            'wait_time_io',
            'wait_time_total',
            'throughput',
            'duration',
            'status'
        ]

        self.prepare_report('requests', self.fieldnames)


        self.flush_filter = 0


        pass


    def prepare_report(self, name, fieldnames):

        if name in self.reports:
            print("ERROR: Report can not be create as a report with that name alread exists:", name)
            exit(1)

        csv_filepath = "%s/%s.csv" % (self.filepath, name)
        csvfile = open(csv_filepath, 'w')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')
        writer.writeheader()
        
        print("CSV written to: %s" % csv_filepath)
        self.reports[name] = {'csvfile': csvfile, 'csv_filepath': csv_filepath, 'writer': writer, 'fieldnames': fieldnames}




    def add_report_row(self, name, dic):
        #print("add_report_row", name, dic)
        #print(self.reports)

        if name not in self.reports:
            print("ERROR: Report can not be create as a report with that name alread exists.")
            exit(1)
        else:
            self.reports[name]['writer'].writerow(dic)

            # log only every 
            self.flush_filter += 1
            if self.flush_filter % 200 != 0:
                self.reports[name]['csvfile'].flush()

    def write_requests(self, requests):
      
        for request in requests:

            dic = dict.fromkeys(self.reports['requests']['fieldnames'])

            # write request flow history?
            # TODO: uncomment if batch processing of unwritten requests may exist
            #self.write_request_flow_history(request)

            # TODO: 
            # duration and throughput calculations are in terms of total
            # request turnaroun is that really desired? "real" network throughput also matters
            duration = request.time_finished - request.time_occur
            
            
            
            dic['occur'] = str(request.time_occur)
            dic['finish'] = str(request.time_finished)

            #dic['duration'] = duration.total_seconds()
            dic['duration'] = str(duration)

            dic['megabytes'] = request.attr['size']
            dic['status'] = request.status

            if duration.total_seconds() == 0.0:
                dic['throughput'] = None
            else:
                dic['throughput'] = request.attr['size'] / duration.total_seconds()

            dic['type'] = request.attr['type']
            #dic[''] = 
            
            #print("DIC DIC DIC DIC DIC DIC", dic)


            #print("CSV written to: %s" % self.reports['requests']['csv_filepath'])
            #print(dic)
            
            self.add_report_row('requests', dic)

        pass


    def write_request_flow_history(self, request):
        """docstring for write_requests"""
      
        fieldnames = [
            'time',
            'throughput'
        ]

        # ensure path exists
        path = "%s/requests" % (self.filepath)
        if not os.path.exists(path):
            os.makedirs(path)

        # prepare filenames and path
        request_filename = str(hex(id(request))) + '.csv'
        request_filepath = "%s/%s" % (path, request_filename)

        with open(request_filepath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quotechar='"')

            writer.writeheader()

            for flow in request.flows:
                dic = dict.fromkeys(fieldnames)

                dic['time'] = str(flow['time'])
                dic['throughput'] = flow['max_flow']

                #print(dic)
                writer.writerow(dic)

        print("CSV written to: %s" % request_filepath)

        pass



