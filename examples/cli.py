#!/usr/bin/env python3

# ----- Imports --------------------------------------------------------------

import argparse
import tinyAPI
from tinyAPI.base.services.cli import cli_main

# ----- Configuration --------------------------------------------------------

args = argparse.ArgumentParser()
args.add_argument('required_arg', help='This argument is required.')
args.add_argument('--optional_arg', help='This argument is optional.')

# ----- Main -----------------------------------------------------------------

def main(cli):
    '''The main program you want the CLI to execute.  The cli parameter here
       is an instance of cli.CLI.'''
    cli.draw_header('My CLI')
    print(cli.args.required_arg)

# ----- Instructions ---------------------------------------------------------

cli_main(args, main)
