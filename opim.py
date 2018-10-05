#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
opim.py

Copyright (c) 2018 Augusto Rallo and Márcio Pessoa

Author: Augusto Rallo <augusto.nascimento@telefonica.com>
Author: Marcio Pessoa <marcio.pessoa@telefonica.com>
Contributors: none

Change log: Check CHANGELOG.md file.

"""

import argparse
import json
import os
import sys
from file import File


class UserArgumentParser():
    """
    https://docs.python.org/2/library/argparse.html
    http://chase-seibert.github.io/blog/
    """

    def __init__(self):
        self.program_name = "OPIM"
        self.program_version = "0.00b"
        self.program_date = "2018-09-14"
        self.program_description = "Open Platform Infrastructure Management"
        self.program_copyright = "Copyright (c) 2018 " + \
                                 "Augusto Rallo and Marcio Pessoa"
        self.program_license = "undefined. There is NO WARRANTY."
        self.program_website = "http://example.com/"
        self.program_contact = "Example <contact@example.com>"
        self.debug = True
        self.config_file = os.path.join(os.getenv('OPIM_PATH', ''),
                                        'opim.json')
        header = ('opim <command> [<args>]\n\n' +
                  'commands:\n' +
                  '  check          just check and display\n' +
                  '  upload         check and upload\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  opim -f opim.json\n')
        self.version = (self.program_name + " " + self.program_version + " (" +
                        self.program_date + ")")
        epilog = (examples + '\n' + footer)
        parser = argparse.ArgumentParser(
            prog=self.program_name,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=epilog,
            add_help=True,
            usage=header)
        parser.add_argument('command', help='command to run')
        parser.add_argument('-V', '--version', action='version',
                            version=self.version,
                            help='show version information and exit')
        if len(sys.argv) < 2:
            self.check()
            sys.exit(False)
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            sys.exit(True)
        getattr(self, args.command)()

    def check(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' check',
            description='just check and display')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info')
        args = parser.parse_args(sys.argv[2:])
        self.config = File()
        self.config.load(self.config_file, 'json')
        self.__hosts_walk()
        sys.exit(False)

    def __host_reset(self):
        '''Set default values'''
        defaults = self.config.get()['host']["_default"]
        host = {}
        host["description"] = defaults["description"]
        host["protocol"] = defaults["protocol"]
        host["port"] = defaults["port"]
        host["warning"] = defaults["warning"]
        host["critical"] = defaults["critical"]
        host["command"] = defaults["command"]
        return host

    def __hosts_walk(self):
        for name in self.config.get()["host"]:
            items = self.config.get()["host"][name]
            host = self.__host_reset()
            host["enable"] = items["enable"]
            if not host["enable"]:
                continue
            host["name"] = name
            host["description"] = items["description"]
            host["address"] = items["address"]
            host["port"] = items["port"]
            host["protocol"] = items["protocol"]
            # host["warning"] = items["warning"]
            # host["critical"] = items["critical"]
            if self.debug:
                print("Host: " + host["name"])
                print("    Description: " + host["description"])
                print("    Address: " + str(host["address"]) + ":" +
                      str(host["port"]))
                print("    Command:" + host["command"])
                print("    Thresholds:")
                print("        Warning: " + str(host["warning"]))
                print("        Critical: " + str(host["critical"]))
            command = self.config.get()["command"][host["command"]]
            command["line"] = os.path.join(command["path"], command["file"]) + \
                              command["options"]
            print command["line"]
            # return_code = os.system(command["line"])
            print


def main():
    UserArgumentParser()


if __name__ == '__main__':
    main()
