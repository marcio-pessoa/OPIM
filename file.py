"""
device_properties.py

Copyright (c) 2018 Augusto Rallo and Marcio Pessoa

Author: Augusto Rallo <augusto.nascimento@telefonica.com>
Author: Marcio Pessoa <marcio.pessoa@telefonica.com>
Contributors: none

Change log:
2018-06-29
        * Version: 0.01b
        * Added: Support to JSON files.

"""

import sys
import json
import os


class File:
    def __init__(self):
        self.version = '0.01b'
        self.reset()

    def reset(self):
        self.data = None

    def load(self, file, type):
        # Open file
        if not file:
            print('File definition missing.')
            sys.exit(True)
        try:
            f = open(file, 'r')
        except IOError as err:
            print(str(err))
            sys.exit(True)
        # Set file type and format
        if type == 'json':
            data = f.read()
            self.json_load(data)
            self.json_check()
            # self.json_info()
        f.close()

    def get(self):
        return self.data

    def json_load(self, data):
        self.reset()
        try:
            self.data = json.loads(data)
        except ValueError as err:
            print(str(err))
            sys.exit(True)

    def json_info(self):
        hosts = 0
        try:
            hosts = len(self.data["host"])
        except BaseException:
            pass
        print('Hosts: ' + str(hosts))

    def json_check(self):
        pass
