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
export interval="${INTERVAL:-3600}"
export max_age="${MAX_AGE:-86400}"
export threshold="${THRESHOLD:-0.05}"
export k="${K:-1}"

# settings for witness_monitor.py
export witness_pubkey="$WITNESS_PUBKEY"
export miss_window="${MISS_WINDOW:-3600}"
export allowed_misses="${ALLOWED_MISSES:-1}"

render_templates
exec "$@"
