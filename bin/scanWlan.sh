#!/usr/bin/env bash

DATAFILEPREFIX=/tmp/crackdump*

rm -f ${DATAFILEPREFIX}*

sudo airmon-ng start wlan1
sudo airodump-ng --uptime --manufacturer --showack --beacons --berlin 20 --output-format csv --write /tmp/crackdump --write-interval 10 wlan1
