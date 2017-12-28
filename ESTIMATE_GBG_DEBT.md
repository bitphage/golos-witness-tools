estimate\_gbg\_debt.py
======================

This script is intended to estimate following values:

* **Possible minimal price of GBG/GOLOS.** This price limits GBG debt to 10% of GOLOS market cap. Witnesses just can't set lower price than that.
* **Percent GBG.** This value is shows current system debt size. It is ratio of `sbd\_supply/median_price / virtual supply`
* **GBG print rate.** This value show the which percent of 1/2 author's reward will go to GBG. The remain will go to the GOLOS.
* **Approximate BTC/GOLOS price at 10%-debt point.** How low market price should become to reach 10% system debt.

System logic
------------

The following describes golosd logic you can find in `libraries/chain/database.cpp`.

* When GBG percent is below STEEMIT\_SBD\_START\_PERCENT (2% currently), GBG print rate is 100%.
* When GBG percent is above STEEMIT\_SBD\_STOP\_PERCENT (5% currently), GBG printing is completely shut off.
* When GBG percent is between START and STOP, GBG print rate varies linearly depending on difference between 5-2. E.g.,
at *percent GBG* 3.5 *print rate* will be 50%.

So, STEEMIT\_SBD\_START\_PERCENT defines a point when system start descreasing of GBG printing, and STEEMIT\_SBD\_STOP\_PERCENT defines a point when GBG printing should be stopped.
