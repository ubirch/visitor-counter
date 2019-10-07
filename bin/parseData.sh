#!/usr/bin/env bash

function usage {
    echo $0 ENV
    exit 1
}

DATAFILE=/tmp/crackdump-01.csv

PARSER="tail -f python3 ./src/visitorCounter.py -env $ENV -cid $CID -pw $PWD"
