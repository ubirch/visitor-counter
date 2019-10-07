#!/usr/bin/env bash

function usage {
    echo $0 ENV
    exit 1
}

if [[ ! -z $1 ]]; then
    ENV=$1
    shift
else
    usage
fi

DATAFILEPREFIX=/tmp/crackdump*
rm ${DATAFILEPREFIX}*

sudo airmon-ng start wlan1
sudo airodump-ng --uptime --manufacturer --showack --beacons --berlin 20 --output-format csv --write /tmp/crackdump --write-interval 10 wlan1
