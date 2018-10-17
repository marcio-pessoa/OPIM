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
from socket import gethostname
from subprocess import call, check_output, CalledProcessError, Popen, PIPE
from file import File


class UserArgumentParser():
    """
    https://docs.python.org/2/library/argparse.html
    http://chase-seibert.github.io/blog/
    """

    def __init__(self):
        self.program_name = "OPIM"
        self.program_version = "0.02b"
        self.program_date = "2018-10-17"
        self.program_description = "Open Platform Infrastructure Management"
        self.program_copyright = "Copyright (c) 2018 " + \
                                 "Augusto Rallo and Marcio Pessoa"
        self.program_license = "undefined. There is NO WARRANTY."
        self.program_website = "http://example.com/"
        self.program_contact = "Example <contact@example.com>"
        self.debug = False
        self.status = ["OK", "Warning", "Critical", "Unknown"]
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
        self.__services_walk()
        sys.exit(False)

    def upload(self):
        parser = argparse.ArgumentParser(
            prog=self.program_name + ' upload',
            description='check and upload')
        parser.add_argument(
            '-v', '--verbosity', type=int,
            default=1,
            choices=[0, 1, 2, 3],
            help='verbose mode, options: ' +
                 '0 Quiet, 1 Errors (default), 2 Warnings, 3 Info')
        args = parser.parse_args(sys.argv[2:])
        self.config = File()
        self.config.load(self.config_file, 'json')
        self.__services_walk(True)
        sys.exit(False)

    def __service_reset(self):
        '''Set default values'''
        defaults = self.config.get()["service"]["_default"]
        service = {}
        service["description"] = defaults["description"]
        service["protocol"] = defaults["protocol"]
        service["port"] = defaults["port"]
        service["warning"] = defaults["warning"]
        service["critical"] = defaults["critical"]
        service["command"] = defaults["command"]
        return service

    def __services_walk(self, upload=False):
        for name in self.config.get()["service"]:
            items = self.config.get()["service"][name]
            service = self.__service_reset()
            service["enable"] = items["enable"]
            if not service["enable"] or \
               name == "_default":
                continue
            # Load main arguments
            service["name"] = name
            service["description"] = items["description"]
            service["address"] = items["address"]
            service["port"] = items["port"]
            service["protocol"] = items["protocol"]
            # Try to load optional arguments
            try:
                service["warning"] = items["warning"]
            except BaseException:
                pass
            try:
                service["critical"] = items["critical"]
            except BaseException:
                pass
            if self.debug:
                print("Service: " + service["name"])
                print("    Description: " + service["description"])
                print("    Address: " + str(service["address"]) + ":" +
                      str(service["port"]))
                print("    Command: " + service["command"])
                print("    Thresholds:")
                print("        Warning: " + str(service["warning"]))
                print("        Critical: " + str(service["critical"]))
            (service["state"], service["output"]) = self.__check_run(service)
            if self.debug:
                print("Status: " + self.status[service["state"]])
            print("Output: " + service["output"])
            sys.stdout.flush()
            # Send results to NRDP server
            if upload:
                self.__send_nrdp(service)
            if self.debug:
                print

    def __check_run(self, service):
        # Build command line
        command = self.config.get()["command"][service["command"]]
        command["line"] = os.path.join(command["path"], command["file"])
        command["line"] += " " + command["options"]
        command["line"] = command["line"].replace("$HOSTADDRESS$",
                                                  service["address"])
        command["line"] = command["line"].replace("$ARG1$",
                                                  str(service["warning"]))
        command["line"] = command["line"].replace("$ARG2$",
                                                  str(service["critical"]))
        command["line"] = command["line"].replace("$ARG3$",
                                                  str(service["port"]))
        if self.debug:
            print("Command line: " + command["line"])
        # Run check command
        print("Checking: " + service["name"] + "..."),
        sys.stdout.flush()
        p = Popen(command["line"].split(" "), stdout=PIPE)
        (output, err) = p.communicate()
        output = output.strip('\n')
        state = p.wait()
        return (state, output)

    def __send_nrdp(self, service):
        nagios = self.config.get()["nagios"]
        nagios["url"] = nagios["protocol"] + \
                        nagios["address"] + \
                        nagios["service"]
        command = "/opt/telefonica/opim/send_nrdp.py" + \
                  " --url=" + nagios["url"] + \
                  " --token=" + nagios["token"] + \
                  " --hostname=" + gethostname() + \
                  " --service=" + service["name"] + \
                  " --state=" + str(service["state"]) + \
                  " --output='" + str(service["output"]) + "'"
        if self.debug:
            print("Command send: " + command)
        call(command, shell=True)


def main():
    UserArgumentParser()


if __name__ == '__main__':
    main()
