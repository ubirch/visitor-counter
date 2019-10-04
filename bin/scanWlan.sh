#!/usr/bin/env bash

function usage {
    echo $0 ENV CID PWD
}

if [[ -z $1 ]]; then
    ENV=$1
    shift
else
    usage
fi

if [[ -z $1 ]]; then
    CID=$1
    shift
else
    usage
fi

if [[ -z $1 ]]; then
    PWD=$1
    shift
else
    usage
fi

EXPORTER="python3 ./src/visitorCounter.py -env $ENV -cid $CID -pw $PWD"

airmon-ng start wlan1
#airodump-ng --uptime --manufacturer --showack --beacons --berlin 20 --output-format csv --write /tmp/crackdump --write-interval 10 wlan1
airodump-ng --uptime --manufacturer --showack --beacons --berlin 20 wlan1 |`${EXPORTER}`
