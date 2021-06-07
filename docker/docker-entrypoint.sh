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
export price_source="${SOURCE:-graphene}"
export node_gph="${NODE_GPH:-"
  - wss://node.gph.ai
  - wss://node.hk.graphene.fans
  "
}"
export markets="${MARKETS:-"
  - RUDEX.GOLOS/GPH
  - RUDEX.GOLOS/RUDEX.BTC
  - RUDEX.GOLOS/RUDEX.USDT"
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
