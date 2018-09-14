#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
xc.py

Copyright (c) 2018 Augusto Rallo and Márcio Pessoa

Author: Augusto Rallo <augusto.rallo@telefonica.com>
Author: Marcio Pessoa <marcio.pessoa@telefonica.com>
Contributors: none

Change log: Check CHANGELOG.md file.

"""

import sys
import argparse


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
        self.services_file = os.path.join(os.getenv('HOME', ''),
                                          'services.json')
        header = ('xc <command> [<args>]\n\n' +
                  'commands:\n' +
                  '  check          just check and display\n' +
                  '  upload         check and upload monitoring data\n\n')
        footer = (self.program_copyright + '\n' +
                  'License: ' + self.program_license + '\n' +
                  'Website: ' + self.program_website + '\n' +
                  'Contact: ' + self.program_contact + '\n')
        examples = ('examples:\n' +
                    '  opim -f services.json\n')
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
            self.gui()
            sys.exit(False)
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            echoln('Unrecognized command')
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
        sys.exit(False)


def main():
    UserArgumentParser()


if __name__ == '__main__':
    main()
