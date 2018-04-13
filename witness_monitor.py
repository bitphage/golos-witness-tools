#!/usr/bin/env python

import sys
import json
import argparse
import logging
import yaml
import time
from datetime import datetime
from datetime import timedelta

from piston import Steem

import functions

log = logging.getLogger('functions')

def main():

    parser = argparse.ArgumentParser(
            description='Monitor missed blocks for specified witness and switch key on misses',
            epilog='Report bugs to: https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-d', '--debug', action='store_true',
            help='enable debug output'),
    parser.add_argument('-c', '--config', default='./witness_monitor.yml',
            help='specify custom path for config file')
    args = parser.parse_args()

    # create logger
    if args.debug == True:
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

    golos = Steem(node=conf['node'], keys=conf['keys'])

    # do not begin monitoring until node will not get synced!
    while True:
        props = golos.info()
        chain_time = datetime.strptime(props['time'], '%Y-%m-%dT%H:%M:%S')
        time_diff = datetime.utcnow() - chain_time
        if time_diff.total_seconds() > 6:
            log.warning('node out of sync, timediff: {}, waiting...'.format(time_diff.total_seconds()))
            time.sleep(60)
        else:
            break

    # get current miss count to begin with
    miss_count = functions.get_witness(golos, conf['witness'])['total_missed']
    log.info('starting monitoring, current miss count: {}'.format(miss_count))

    miss_window_start_time = datetime.now()
    miss_window = eval(str(conf['miss_window']))
    prev_key = str()

    while True:

        try:
            w = functions.get_witness(golos, conf['witness'])
        except Exception as e:
            log.error('failed to get witness data: %s', e)
            time.sleep(63)
            continue
        current_miss_count = w['total_missed']
        miss_diff = current_miss_count - miss_count
        log.debug('current miss diff: {}'.format(miss_diff))

        # too much misses and witness running at another node and previous key is not ours
        if miss_diff > conf['allowed_misses'] and \
           w['signing_key'] != conf['witness_pubkey'] and \
           prev_key != conf['witness_pubkey']:

            # switch witness key to us
            log.info('switching witness key, miss_diff is: {} > {}'.format(miss_diff, conf['allowed_misses']))
            try:
                functions.update_witness(golos, conf['witness_pubkey'], w['url'], w['props'], conf['witness'])
            except Exception as e:
                log.error('failed to switch key: %s', e)
            else:
                # reset miss_count after switch
                miss_count = current_miss_count

        now = datetime.now()
        time_delta = now - miss_window_start_time
        if time_delta.total_seconds() > miss_window:
            log.debug('miss_window ended, beginning a new one')
            # miss_window ended, begin next miss_window
            miss_window_start_time = datetime.now()
            # reset miss_count once per miss_window
            miss_count = current_miss_count

        # remember current signing key as `previous key`
        prev_key = w['signing_key']

        # try to check miss counter at each round
        time.sleep(63)

if __name__ == '__main__':
    main()
