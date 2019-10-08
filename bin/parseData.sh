#!/usr/bin/env bash

function usage {
    echo $0 ENV CID PW
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

if [[ -f "../data/crackdump-01.csv" ]]; then
    DATAFILE=../data/crackdump-01.csv
else
    DATAFILE=/tmp/crackdump-01.csv
fi

. ./.venv/bin/activate

cd src
tail -f ${DATAFILE}|python3 visitorCounter.py -env $ENV -cid $CID -pw $PWD -db ../macsdb/macsdb.json
