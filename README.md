golos-witness-tools
===================

This is a set of scripts for golos blockchain witness operators.

Scripts
-------

* [**update\_price\_feed.py**](PRICEFEED.md): script to update GBG/GOLOS price feed in golos blockchain
* [**update\_witness.py**](UPDATE_WITNESS.md): script to manipulate witness data in the blockchain
* [**witness_monitor.py**](WITNESS_MONITOR.md): script to monitor block misses and autoswitch nodes
* **get\_witness.py**: script to obtain current info for specified witness
* **get\_witnesses.py**: script to display known witnesses, sorted by votes
* **get\_miner\_queue.py**: script to display miner queue
* [**estimate\_gbg\_debt.py**](ESTIMATE_GBG_DEBT.md): script to estimate system debt in GBG
* **get\_median\_props.py**: script to display current votable parameters
* **get\_feed\_history.py**: script to obtain median price history
* **inflation.py**: script to model inflation

Requirements
------------

* golos node 0.18+

Installation using pipenv
-------------------------

1. Install [pipenv](https://docs.pipenv.org/).
2. Run the following code

```
pipenv install
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

To manually build docker image:

```
docker build -t vvk123/golos-witness-tools:latest .
```
