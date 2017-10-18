update\_price\_feed.py
======================

Script to update GBG/GOLOS price feed in golos blockchain.

No `cli_wallet` required!

Configuration
-------------

First, you need to configure script by modifying configuration template. Let's create a config:

`cp update_price_feed.yml.example update_price_feed.yml`

Then, you need to change at least these parameters:

* **node** - golos node to connect
* **witness** - your witness
* **keys** - private active key of your witness

Modes
-----

This scripts can be used in several modes:

* Dry-run mode: `./update_price_feed.py --dry-run` will perform price calculations, but no transactions will be sent
* One-time run, just launch `./update_price_feed.py` without arguments and it will update price feed and exit.
* Continuous mode. `./update_price_feed.py --monitor` will start script and it will continue working in infinite loop mode
  performing periodical price recalculations and updates.

Cron friendly
-------------

You may wish to run this script on "host system" without any virtualization just from cron without any output.
Example:

```
01 * * * * cd /opt/golos-witness-tools/ && ./venv/bin/python update_price_feed.py --quiet
```

Docker friendly
---------------

Example exec in plain docker:

```
docker run -it --rm -e WITNESS=foo -e KEY=WIF_PRIVKEY golos-witness-tools:latest ./update_price_feed.py --dry-run
```

How it works
------------

1 GBG price should be equal to price of 1 mg gold.
1 GBG is a backed asset of GOLOS blockchain. Blockchain may buy your GBG for GOLOS threating 1 GBG price as price of 1
mg gold.

To calculate GBG/GOLOS price, we need following variables:

* price of 1 mg of gold. Script tries to get USD/gold price from goldprice.org. In case of failure, Russian Central Bank
  price is used. The price provided by Russian Central Bank is in RUB, so we're recalculating it to USD/gold.
* price USD/BTC. We need this price because GOLOS is exchanged to BTC and not to USD directly. We use coinmarketcap.org
  as primary source and some exchanges as a backup source.
* price BTC/GOLOS. Again, we're using coinmarketcap.org as a primary source and bittrex as a backup.


Multiple instances
------------------

To keep your published feed always up-to-date, you may run `update_price_feed.py` from multiple machines. Multiple
instances will not conflict with each other because script performs price comparison with previously published price.

