#!/usr/bin/env python3
from classes.logger import Logger
import csv
from random import randint

log = Logger().log

class Proxy:

    def __init__(self):
        self.proxies = self.importProxy()
        self.countOG = len(self.proxies) - 1
        self.count = 0
        if len(self.proxies) is not 0:
            self.count = randint(0, len(self.proxies) - 1)

    def importProxy(self):

        more_results = list()
        with open('config/proxies.txt', newline='') as inputfile:
            for row in csv.reader(inputfile):
                splitted = row[0].split(":")

                # IP:Port
                if len(splitted) == 2:
                    prox_obj = {
                        'http': 'http://' + row[0],
                        'https': 'https://' + row[0]
                    }
                    more_results.append(prox_obj)

                # IP:Port:User:Password
                if len(splitted) == 4:
                    prox_obj = {
                        'http': 'http://' + splitted[2] + ':' + splitted[3] + '@' + splitted[0] + ':' + splitted[1],
                        'https': 'https://' + splitted[2] + ':' + splitted[3] + '@' + splitted[0] + ':' + splitted[1]
                    }
                    more_results.append(prox_obj)
        return more_results

    def getProxy(self):
        return self.proxies

    def countProxy(self):
        if self.count == 0:
            self.count = self.countOG
        else:
            self.count = self.count - 1
        return self.count

