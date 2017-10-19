#!/usr/bin/env python

# This script is inspired by roelandp script https://github.com/roelandp/golospricefeed

import sys
import requests
import argparse
import logging
import time
import yaml

from datetime import date
from datetime import datetime
from datetime import timedelta
from xml.dom.minidom import parseString
from piston import Steem
from piston.converter import Converter
from piston.witness import Witness

def get_price_gold_goldpriceorg():
    """ returns gold price in USD from goldprice.org """

    price_troyounce = 0;
    try:
        r = requests.get("http://data-asg.goldprice.org/GetData/USD-XAU/1").json()
        price_troyounce = float(r[0].split(',')[1])
    except Exception as e:
        log.error(e)
        return False
    gram_in_troyounce = 31.1034768
    price_mg = price_troyounce / gram_in_troyounce / 1000
    return price_mg

def get_price_gold_cbr():
    """ get gold price from Russian Central Bank; return value is RUB """

    one_day = timedelta(days=1)
    today = date.today()
    yesterday = today - one_day
    # cbr metall codes: (1 - gold, 2 - silver, 3 - platinum, 4 - palladium)
    # cbr may return an empty value on Monday, so request 2 days history
    payload = {'date_req1': yesterday.strftime('%d/%m/%Y'), 'date_req2': today.strftime('%d/%m/%Y')}
    try:
        r = requests.get('http://www.cbr.ru/scripts/xml_metall.asp', params=payload)
    except Exception as e:
        log.error(e)
        return False

    dom = parseString(r.text)
    
    price = []
    for element in dom.getElementsByTagName('Record'):
        if element.getAttribute('Code') == '1':
            price.append(element.getElementsByTagName('Buy')[0].childNodes[0].data.split(',')[0])

    # return value is grams, so divide to 1000
    return(float(price[0])/1000)

def get_rub_usd_price():
    """ get RUB/USD price from Russian Central Bank API mirror """

    try:
        r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    except Exception as e:
        log.error(e)
        return False

    return(r.json()['Valute']['USD']['Value'])

def get_price_gold_cbr_in_usd():
    """ calculate gold price in USD based on cbr.ru rates """

    rub_gold_price = get_price_gold_cbr()
    rub_usd_price = get_rub_usd_price()
    if rub_usd_price:
        usd_gold_price = rub_gold_price/rub_usd_price
        return usd_gold_price
    else:
        return False

def get_price_gold():
    """ Wrapper function. Try goldprice.org, if failed try Russian Central Bank """

    price = get_price_gold_goldpriceorg()
    if price:
        log.debug('USD/gold price taken from goldprice.org')
        return price
    price = get_price_gold_cbr_in_usd()
    if price:
        log.debug('USD/gold price taken from Russian Central Bank')
        return price
    else:
        log.critical('failed to obtain USD/gold price from any source, cannot continue')
        sys.exit(1)

def get_price_usd_btc_exchanges():

    """ returns average BTC/USD price across some exchanges"""
    prices = {}
    try:
        r = requests.get("https://api.bitfinex.com/v1/pubticker/BTCUSD").json()
        prices['bitfinex'] = {'price': float(r['last_price']), 'volume': float(r['volume'])}
    except:
        pass
    try:
        r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker").json()
        prices['coinbase'] = {'price': float(r['price']), 'volume': float(r['volume'])}
    except:
        pass
    try:
        r = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/").json()
        prices['bitstamp'] = {'price': float(r['last']), 'volume': float(r['volume'])}
    except:
        pass
    if not prices:
       return 0
    total_usd = 0
    total_btc = 0
    for p in prices.values():
        total_usd += p['price'] * p['volume']
        total_btc += p['volume']
    avg_price = total_usd / total_btc
    return avg_price

def get_price_bittrex(cur1, cur2):
    """ Calculate cur1 to cur2 price based on exchangers history """
    try:
        payload = {'market': '{}-{}'.format(cur1, cur2)}
        bt_h = requests.get("https://bittrex.com/api/v1.1/public/getmarkethistory", params=payload)
        bt_hist = bt_h.json()
        cur1_quantity = 0
        cur2_quantity = 0
        for i in range(200):
            cur1_quantity += bt_hist["result"][i]["Quantity"]
            cur2_quantity += bt_hist["result"][i]["Total"]
    except Exception as e:
        log.error(e)
        log.error("Error in fetching Bittrex market history")
        sys.exit(1)

    price = cur1_quantity/cur2_quantity
    return price

def get_price_usd_btc_coinmarketcap():
    """ returns USD/BTC price from coinmarketcap.org """
    try:
        r = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/')
    except Exception as e:
        log.error(e)
        return False
    price = r.json()[0]['price_usd']
    return price


def get_price_btc_golos_coinmarketcap():
    """ returns BTC/GOLOS price from coinmarketcap.org """
    try:
        r = requests.get('https://api.coinmarketcap.com/v1/ticker/golos/')
    except Exception as e:
        log.error(e)
        return False
    price = r.json()[0]['price_btc']
    return price

def get_price_btc_gbg_coinmarketcap():
    """ returns BTC/GBG price from coinmarketcap.org """
    try:
        r = requests.get('https://api.coinmarketcap.com/v1/ticker/golos-gold/')
    except Exception as e:
        log.error(e)
        return False
    price = r.json()[0]['price_btc']
    return float(price)

def get_price_usd_btc():
    """ wrapper function to obtain USD/BTC price """

    price = get_price_usd_btc_coinmarketcap()
    if price:
        log.debug('USD/BTC price taken from coinmarketcap.org')
        return float(price)
    price = get_price_usd_btc_exchanges()
    if price:
        return float(price)
    else:
        log.critical('failed to obtain USD/BTC price from any source, cannot continue')
        sys.exit(1)

def get_price_btc_gbg():
    """ wrapper function to obtain BTC/GBG price """

    price = get_price_btc_gbg_coinmarketcap()
    if price:
        log.debug('BTC/GBG price taken from coinmarketcap.org')
        return float(price)
    price = get_price_bittrex('BTC', 'GBG')
    if price:
        return float(price)
    else:
        log.critical('failed to obtain BTC/GBG price from any source, cannot continue')
        sys.exit(1)

def get_price_btc_golos():
    """ wrapper function to obtain BTC/GOLOS price """

    price = get_price_btc_golos_coinmarketcap()
    if price:
        log.debug('BTC/GOLOS price taken from coinmarketcap.org')
        return float(price)
    price = get_price_bittrex('BTC', 'GOLOS')
    if price:
        return float(price)
    else:
        log.critical('failed to obtain BTC/GOLOS price from any source, cannot continue')
        sys.exit(1)


def calculate_gbg_golos_price():

    # market price USD/gold
    price_mg_gold = get_price_gold()
    log.info('USD/gold: %s', price_mg_gold)

    # market price USD/BTC
    usd_btc = get_price_usd_btc()
    log.info('USD/BTC: %s', usd_btc)

    # market price BTC/GOLOS
    btc_golos = get_price_btc_golos()
    log.info('BTC/GOLOS: %s', format(btc_golos, '.8f'))

    # market price BTC/GBG just for analytics
    price_btc_gbg = get_price_btc_gbg()
    log.info('BTC/GBG: %s', format(price_btc_gbg, '.8f'))

    # calculated price BTC/gold just for analytics
    price_btc_gold = price_mg_gold/usd_btc
    log.info('BTC/gold: %s', format(price_btc_gold, '.8f'))

    # BTC/GBG / BTC/gold rate just for analytics
    gbg_gold_rate = price_btc_gbg/price_btc_gold
    log.info('GBG/gold rate: %s', gbg_gold_rate)

    # calculated price USD/golos just for analytics
    price_usd_golos = btc_golos*usd_btc
    log.info('USD/GOLOS: %s', price_usd_golos)

    # how many mgs of gold in 1 GOLOS == GOLOS/GBG (1 GBG == 1 mg gold)
    price_gold_golos = price_usd_golos / price_mg_gold
    log.info('GBG/GOLOS: %s', price_gold_golos)

    return price_gold_golos

def get_median_price(steem_instance):
    """ get current median GBG/GOLOS price from network """

    cv = Converter(steem_instance)
    price = cv.sbd_median_price()
    log.info('Current median price: %s', price)
    return price

def get_old_price(steem_instance, witness):
    """ obtain current published price for witness """

    w = Witness(witness, steem_instance)
    base = float(w['sbd_exchange_rate']['base'].split()[0])
    quote = float(w['sbd_exchange_rate']['quote'].split()[0])

    # whether witness not exists yet, return 0
    if quote == 0:
        return 0
    else:
        price = base/quote
        log.info('Old price: %s', price)
        return price

def last_price_too_old(steem_instance, witness, max_age):
    """ Check last price update time and return True or False """

    w = Witness(witness, steem_instance)
    l = w['last_sbd_exchange_update']
    last_update = datetime.strptime(l, '%Y-%m-%dT%H:%M:%S')

    delta = datetime.utcnow() - last_update
    if delta.seconds > max_age:
        return True
    else:
        return False

def publish_price(steem_instance, price):
    """ broadcast calculated price to the network """

    # we should publish feed in format 0.000
    final_gbg_price = format(price, '.3f')
    log.info('Price to publish: %s' % final_gbg_price)
    try:
        steem_instance.witness_feed_publish(price, quote='1.000')
    except Exception as e:
        log.error(e)
        return False


def main():

    parser = argparse.ArgumentParser(
            description='golos price feed updater',
            epilog='Report bugs to https://github.com/bitfag/golos-witness-tools/issues')
    parser.add_argument('-c', '--config', default='./update_price_feed.yml',
            help='specify custom path for config file')
    parser.add_argument('-n', '--dry-run', action='store_true',
        help='calculate prices but do not send transaction to golos network')
    parser.add_argument('-m', '--monitor', action='store_true',
        help='run in continuous mode and update price periodically')

    verbosity_args = parser.add_mutually_exclusive_group()
    verbosity_args.add_argument('-q', '--quiet', action='store_true',
        help='do not show any output except errors, just silently update price feed'),
    verbosity_args.add_argument('-d', '--debug', action='store_true',
        help='enable debug output'),
    args = parser.parse_args()

    # create logger
    global log
    log = logging.getLogger('update_price_feed.py')
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

    # main loop
    while True:
        price = calculate_gbg_golos_price()
        old_price = get_old_price(golos, conf['witness'])
        median_price = get_median_price(golos)

        if args.dry_run:
            log.info('--dry-run mode, not publishing feed')
        else:
            # check whether our price is too old
            last_price_update_too_old = last_price_too_old(golos, conf['witness'], conf['max_age'])
            if last_price_update_too_old:
                log.info('Our last price was updated long ago, forcing update')
                publish_price(golos, price)
            else:
                # check for price difference between our old price and new price
                diff = abs(old_price - price)
                if diff > conf['threshold']:
                    log.info('publishing price, difference is: %s', diff)
                    publish_price(golos, price)
                else:
                    log.debug('price difference is too low, not publishing price')

        if args.monitor:
            time.sleep(conf['interval'])
        else:
            sys.exit(0)

if __name__ == '__main__':
    main()
