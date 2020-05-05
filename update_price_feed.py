#!/usr/bin/env python

import argparse
import asyncio
import logging
import sys

import yaml
from golosscripts.feed import FeedUpdater

log = logging.getLogger('golosscripts')


def main():

    parser = argparse.ArgumentParser(
        description='golos price feed updater',
        epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues',
    )
    parser.add_argument('-c', '--config', default='./update_price_feed.yml', help='specify custom path for config file')
    parser.add_argument(
        '-m', '--monitor', action='store_true', help='run in continuous mode and update price periodically'
    )

    publish_args = parser.add_mutually_exclusive_group()
    publish_args.add_argument(
        '-n', '--dry-run', action='store_true', help='calculate prices but do not send transaction to golos network'
    )
    publish_args.add_argument('-f', '--force', action='store_true', help='force update price feed')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help='do not show any output except errors, just silently update price feed',
    ),
    verbosity_args.add_argument('-d', '--debug', action='store_true', help='enable debug output'),
    args = parser.parse_args()

    # create logger
    if args.quiet:
        log.setLevel(logging.ERROR)
    elif args.debug:
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

    feed_updater = FeedUpdater(**conf)

    if args.monitor:
        asyncio.run(feed_updater.run_forever())
    else:
        asyncio.run(feed_updater.publish_price())

    return 0


if __name__ == '__main__':
    sys.exit(main())
