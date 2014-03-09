#!/usr/bin/env python3

# ----- Imports --------------------------------------------------------------

import time
import tinyAPI
from tinyAPI.base.services.cli import cli_main
from tinyAPI.base.services.crypto import DataArmor

# ----- Main ----------------------------------------------------------------

def main(cli):
    cli.header('Data Armor')

    key = '12345678901234567890123456789012'

    data_armor = DataArmor(key, 'Hello World!')
    token = data_armor.lock()

    cli.notice('The armored token is:')
    cli.notice(token, 1)

    data_armor = DataArmor(key, token)

    cli.notice('Unlocking the token should print "Hello World!":')
    cli.notice(data_armor.unlock(), 1)

    cli.notice("Let's TTL expire a token!")
    cli.notice('The delay in execution is a sleep, be patient.')
    cli.notice('After the sleep you should see an exception.')
    cli.notice('It should tell you that the token has expired.')

    data_armor = DataArmor(key, 'Hello World!')
    token = data_armor.lock()

    time.sleep(5)

    DataArmor(key, token).unlock(1)

# ----- Instructions ---------------------------------------------------------

cli_main(main)
