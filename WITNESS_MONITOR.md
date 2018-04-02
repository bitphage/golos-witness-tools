witness\_monitor.py
===================

This script is intended to run as a docker container to perform monitoring of missed blocks and automatically switch witness to the current node whether misses are detected.

Building a redundant witness infrastructure
-------------------------------------------

To achieve witness redundancy you need at least 2 nodes (but you can set up 3 or more).

On the each node you need to configure the same witness but private keys should be different.

node1:

```
witness = "foo"
private-key = key1
```

node2:

```
witness = "foo"
private-key = key2
```

node3:

```
witness = "foo"
private-key = key3
```

**Note**: to generate keys, you can use [generate\_keypair.py](https://github.com/bitfag/golos-scripts) script.

**Never use the same key on different nodes! This will lead to a double-production and chain forks!**

So, having such configuration, you can always choose which node should actually produce blocks.

Imagine your current active signing node is down. So, you just need to update witness to change the signing_key. This can be done by using `witness_update()` API call directly, or using script `update_witness.py` from this package.

Automating switching from failed node to a working one
==================================================

To automate process of switching signing keys, you can use `witness_monitor.py`.

How it works
------------

At every 63 seconds (once per round) the script checks current `total_missed` counter.

There are 2 tunable parameters:

* `miss_window`
* `allowed_misses`

The logic is simple: switch are happening whether there are more misses detected than `allowed_misses` per `miss_window`.

For example, you can allow 2 misses per 1 hour. Whether script detects 3 misses per hour, it will switch signing key.

Example configuration
---------------------

To achieve working configuration, on each node you need:

* golosd itself
* price feed script
* `witness_monitor.py` script

Please look at the example [docker-compose.yml](docker-compose.yml.example) to see how all things are intended to work together.

How it works with nodes > 2
---------------------------

Whether you have more than 2 nodes, in case of current signing node failure, the `witness_monitor.py` on another nodes will detect misses and will perform the key switch.

So, every "backup" node will try to switch block production to itself. Because it will happen with some time difference, only the least node will actually take over.

There are no priorities and you cannot configure in which order your nodes should take over block production. But, actually you can simulate priorities by setting different value for an `allowed_misses` tunable.