#!/bin/sh -e

render_templates()
{
    confd -onetime -backend env
}

# default settings
export node="${NODE:-ws://golos:8091}"
export witness="${WITNESS:-foo}"
export key="${KEY:-key}"
export interval="${INTERVAL:-3600}"
export max_age="${MAX_AGE:-86400}"
export threshold="${THRESHOLD:-0.05}"
export k="${K:-1}"

render_templates
exec "$@"
