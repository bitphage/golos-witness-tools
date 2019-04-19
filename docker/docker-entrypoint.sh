#!/bin/sh -e

render_templates()
{
    confd -onetime -backend env
}

# default common settings
export node="${NODE:-ws://golos:8091}"
export witness="${WITNESS:-foo}"
export key="${KEY:-key}"

# settings for update_price_feed.py
export price_source="${SOURCE:-bitshares}"
export node_bts="${NODE_BTS:-"
  - wss://eu.nodes.bitshares.ws
  - wss://bitshares.openledger.info/ws
  - wss://citadel.li/node
  - wss://api-ru.bts.blckchnd.com
  - wss://api.bts.blckchnd.com"
}"
export markets="${MARKETS:-"
  - RUDEX.GOLOS/BTS
  - RUDEX.GOLOS/RUDEX.BTC
  - RUDEX.GOLOS/RUBLE
  - RUDEX.GOLOS/USD
  - RUDEX.GOLOS/CNY"
}"
export metric="${METRIC:-weighted_average}"
export depth_pct="${DEPTH_PCT:-20}"
export interval="${INTERVAL:-3600}"
export max_age="${MAX_AGE:-86400}"
export threshold_pct="${THRESHOLD_PCT:-10}"
export k="${K:-1}"

# settings for witness_monitor.py
export witness_pubkey="$WITNESS_PUBKEY"
export miss_window="${MISS_WINDOW:-3600}"
export allowed_misses="${ALLOWED_MISSES:-1}"

render_templates
exec "$@"
