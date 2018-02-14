golos-witness-tools
===================

This is a set of scripts for golos blockchain witness operators.

Scripts
-------

* [**update\_price\_feed.py**](PRICEFEED.md): script to update GBG/GOLOS price feed in golos blockchain
* [**update\_witness.py**](UPDATE_WITNESS.md): script to manipulate witness data in the blockchain
* **get\_witness.py**: script to obtain current info for specified witness
* [**estimate\_gbg\_debt.py**](ESTIMATE_GBG_DEBT.md): script to estimate system debt in GBG
* **get\_median\_props.py**: script to display current votable parameters
* **get\_feed\_history.py**: script to obtain median price history

Running scripts in virtualenv
-----------------------------

```
mkdir venv
virtualenv -p python3 venv
source ./venv/bin/activate
pip3 install -r requirements.txt
./update_price_feed.py --dry-run
```

Running scripts in docker
-------------------------

Plain docker example:

```
docker run -it --rm vvk123/golos-witness-tools:latest ./update_price_feed.py --dry-run
```

docker-compose:

* copy docker-compose.yml.example to docker-compose.yml
* adjust environment variables in docker-compose.yml. Look for all env vars in `docker-entrypoint.sh`

```
docker-compose up -d
```
