update\_witness\_.py
======================

This script is useful tool to update your witness information in the blockchain.

Use-cases
---------

1. You can just update your witness info by running `./update_witness.py` without params
2. You can shutdown your witness by executing `./update_witness.py --shutdown`. In this mode you witness signing key will be set to special key `GLS1111111111111111111111111111111114T1Anm` which says to the golos blockchain network "this witness is shutdown, don't use it".


Configuration
-------------

First, you need to configure script by modifying configuration template.

`cp update_witness.yml.example update_witness.yml`

Then, you need to change at least these parameters:

* **node** - golos node to connect
* **witness** - your witness
* **keys** - private active key of your witness account
* **witness_pubkey** - this is the public key of your witness signing account. The private key of this pair you will use as `private-key = ` in golosd `config.ini`. You may generate a keypair using <https://github.com/bitfag/golos-scripts/blob/master/generate_keypair.py>


