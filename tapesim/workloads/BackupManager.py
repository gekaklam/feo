#!/usr/bin/env python3
# -*- coding: utf-8 -*-





class BackupManager(object):
    def __init__(self):
        """

        full: 
            a full copy of the data
            
            + quick recovery
            - high capacity required


        cumulative incremental:
            
            + less capacity required
            ~ slightly slower recovery

        differential incremental:
           
           - slow recovery process


        incremental forever backup:
           
            + no redundant data transmitted from clients to storage, lowest capacity demands
            - not feasable with tape, but ok good with disks
            - highly vulnerable to media errors



        usually hybrid strategies are used



        """


            

        self.unit  = "days"
        self.pivot = "sunday"

        #                         SmtwtfsSmtwtfsSmtwtfsSmtwtfsSmtwtfsSmtwtfsSmtwtfsSmtwtfsSmtwtfsS
        self.strategy_sequence = "fddddddcddddddcddddddcdddddd" # full every month, cummulative weekly, incremental in between

        
        self.backup_targets = []
        self.backup_servers = []
        self.backup_clients = []


        self.backup_catalogue = []


        pass
