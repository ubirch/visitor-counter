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

if [[ ! -z $1 ]]; then
    CID=$1
    shift
else
    usage
fi

if [[ ! -z $1 ]]; then
    PWD=$1
    shift
else
    usage
fi

DATAFILE=/tmp/crackdump-01.csv

tail -f python3 ./src/visitorCounter.py -env $ENV -cid $CID -pw $PWD
