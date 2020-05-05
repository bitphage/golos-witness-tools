#!/usr/bin/env python

import argparse
import logging
import sys

import yaml
from golosscripts.monitor import Monitor

log = logging.getLogger('golosscripts')


def main():

    parser = argparse.ArgumentParser(
        description='Monitor missed blocks for specified witness and switch key on misses',
        epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues',
    )
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    parser.add_argument('-c', '--config', default='./witness_monitor.yml', help='specify custom path for config file')
    args = parser.parse_args()

    # create logger
    if args.debug is True:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # parse config
    with open(args.config, 'r') as ymlfile:
        conf = yaml.safe_load(ymlfile)

    monitor = Monitor(**conf)
    monitor.run_forever()

    return 0


if __name__ == '__main__':
    sys.exit(main())
