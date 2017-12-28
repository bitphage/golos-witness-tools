#!/usr/bin/env python

import argparse
import logging
import yaml

from piston import Steem
from piston.witness import Witness
from datetime import datetime
from datetime import timedelta

log = logging.getLogger('functions')

def update_witness(steem_instance, signing_key, url, props, account):

    log.debug('args: %s', locals())
    try:
        steem_instance.witness_update(signing_key, url, props, account=account)
    except Exception as e:
        log.error(e)
        raise e

def main():

    parser = argparse.ArgumentParser(
            description='golos witness updater',
            epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-c', '--config', default='./update_witness.yml',
            help='specify custom path for config file')
    parser.add_argument('--shutdown', action='store_true',
            help='shutdown witness')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-q', '--quiet', action='store_true',
        help='do not show any output except errors'),
    verbosity_args.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),
    args = parser.parse_args()

    # create logger
    if args.quiet == True:
        log.setLevel(logging.ERROR)
    elif args.debug == True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.load(ymlfile)

    # initialize steem instance
    golos = Steem(node=conf['node'], keys=conf['keys'])

    # set pubkey to special value whether we need to shutdown witness
    if args.shutdown:
        pubkey = 'GLS1111111111111111111111111111111114T1Anm'
    else:
        pubkey = conf['witness_pubkey']

    # update witness
    update_witness(golos, pubkey, conf['url'], conf['props'], conf['witness'])

if __name__ == '__main__':
    main()
