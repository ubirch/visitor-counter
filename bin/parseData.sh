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
    PASSWD=$1
    shift
else
    usage
fi

if [[ -f "./data/crackdump-01.csv" ]]; then
    DATAFILE=../data/crackdump-01.csv
else
    DATAFILE=/tmp/crackdump-01.csv
fi

. ./.venv/bin/activate

cd src
if [[ -f ${DATAFILE} ]]; then
    tail -f ${DATAFILE}| python3 visitorCounter.py -env ${ENV} -cid ${CID} -pw ${PASSWD} -db ../macsdb/macsdb.json
else
    echo no datafile ${DATAFILE}
fi
