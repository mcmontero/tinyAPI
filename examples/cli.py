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
    cli.notice("I've started doing something and everything is OK!")
    cli.notice("now I am doing something related to the previous message", 1)
    cli.warn("You should know that something is amiss.")
    cli.error("Something is really wrong now!")

# ----- Instructions ---------------------------------------------------------

cli_main(main, args)
