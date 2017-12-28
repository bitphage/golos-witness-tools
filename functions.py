import logging
import time
import requests

from xml.dom.minidom import parseString
from datetime import date
from datetime import datetime
from datetime import timedelta

from piston.converter import Converter
from piston.witness import Witness

log = logging.getLogger(__name__)

def get_median_price(steem_instance):
    """ get current median GBG/GOLOS price from network
        :param Steem steem_instance: Steem() instance to use when accesing a RPC
    """

    cv = Converter(steem_instance)
    try:
        price = cv.sbd_median_price()
    except Exception as e:
        log.error(e)
        return False

    log.debug('current median price: %s', price)
    return price


def get_price_gold_goldpriceorg():
    """ returns gold price in USD from goldprice.org """

    price_troyounce = 0;
    try:
        r = requests.get("http://data-asg.goldprice.org/GetData/USD-XAU/1", timeout=5).json()
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
        r = requests.get('http://www.cbr.ru/scripts/xml_metall.asp', params=payload, timeout=5)
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
        r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js', timeout=5)
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
        log.critical('failed to obtain USD/gold price from any source')
        return False

def get_price_usd_btc_exchanges():
    """ returns average BTC/USD price across some exchanges"""

    prices = {}
    try:
        r = requests.get("https://api.bitfinex.com/v1/pubticker/BTCUSD", timeout=5).json()
        prices['bitfinex'] = {'price': float(r['last_price']), 'volume': float(r['volume'])}
    except:
        pass
    try:
        r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/ticker", timeout=5).json()
        prices['coinbase'] = {'price': float(r['price']), 'volume': float(r['volume'])}
    except:
        pass
    try:
        r = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/", timeout=5).json()
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
    """ Calculate cur1 to cur2 price based on bittrex trade history """

    try:
        payload = {'market': '{}-{}'.format(cur1, cur2)}
        bt_h = requests.get("https://bittrex.com/api/v1.1/public/getmarkethistory", params=payload, timeout=5)
        bt_hist = bt_h.json()
        cur1_quantity = 0
        cur2_quantity = 0
        for i in range(100):
            cur1_quantity += bt_hist["result"][i]["Quantity"]
            cur2_quantity += bt_hist["result"][i]["Total"]
    except Exception as e:
        log.error(e)
        log.error("Error in fetching Bittrex market history")
        return False

    price = cur2_quantity/cur1_quantity
    return price

def get_price_usd_btc_coinmarketcap():
    """ returns USD/BTC price from coinmarketcap.org """

    try:
        r = requests.get('https://api.coinmarketcap.com/v1/ticker/bitcoin/', timeout=5)
    except Exception as e:
        log.error(e)
        return False
    price = r.json()[0]['price_usd']
    return price

def get_price_btc_golos_coinmarketcap():
    """ returns BTC/GOLOS price from coinmarketcap.org """

    try:
        r = requests.get('https://api.coinmarketcap.com/v1/ticker/golos/', timeout=5)
    except Exception as e:
        log.error(e)
        return False
    price = r.json()[0]['price_btc']
    return price

def get_price_btc_gbg_coinmarketcap():
    """ returns BTC/GBG price from coinmarketcap.org """

    try:
        r = requests.get('https://api.coinmarketcap.com/v1/ticker/golos-gold/', timeout=5)
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
        log.debug('USD/BTC price taken from exchanges')
        return float(price)
    else:
        log.error('failed to obtain USD/BTC price from any source')
        return False

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
        log.critical('failed to obtain BTC/GBG price from any source')

def get_price_btc_golos():
    """ wrapper function to obtain BTC/GOLOS price """

    price = get_price_btc_golos_coinmarketcap()
    if price:
        log.debug('BTC/GOLOS price taken from coinmarketcap.org')
        return float(price)
    price = get_price_bittrex('BTC', 'GOLOS')
    if price:
        log.debug('BTC/GOLOS price taken from bittrex')
        return float(price)
    else:
        log.error('failed to obtain BTC/GOLOS price from any source')
        return False


def get_witness(steem_instance, witness):
    """ call get_witness_by_account and return Witness object """

    w = Witness(witness, steem_instance)
    return w

def get_old_price(witness_data):
    """ obtain current published price for witness """

    base = float(witness_data['sbd_exchange_rate']['base'].split()[0])
    quote = float(witness_data['sbd_exchange_rate']['quote'].split()[0])

    # whether witness not exists yet, return 0
    if quote == 0:
        return 0
    else:
        price = base/quote
        log.info('Old price: %s', price)
        return price

def last_price_too_old(witness_data, max_age):
    """ Check last price update time and return True or False """

    l = witness_data['last_sbd_exchange_update']
    last_update = datetime.strptime(l, '%Y-%m-%dT%H:%M:%S')
    log.debug('last price update: %s', last_update)
    log.debug('max_age: %s', max_age)

    delta = datetime.utcnow() - last_update
    log.debug('time passed since last update: %s', delta.total_seconds())

    if delta.total_seconds() > max_age:
        log.debug('last_price_too_old(): need price update')
        return True
    else:
        return False

def publish_price(steem_instance, price, account=False):
    """ broadcast calculated price to the network """

    # we should publish feed in format 0.000
    final_gbg_price = format(price, '.3f')
    log.info('Price to publish: %s' % final_gbg_price)
    try:
        steem_instance.witness_feed_publish(final_gbg_price, quote='1.000', account=account)
    except Exception as e:
        log.error(e)
        return False


