golos-witness-tools
===================

This is a set of scripts for golos blockchain witness operators.

Scripts
-------

* [**update\_price\_feed.py**](PRICEFEED.md): script to update GBG/GOLOS price feed in golos blockchain

Running scripts in virtualenv
-----------------------------

```
mkdir venv
virtualenv -p python3 venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

Running scripts in docker
-------------------------

```
docker run -it --rm vvk123/golos-witness-tools:latest ./update_price_feed.py --dry-run
```
