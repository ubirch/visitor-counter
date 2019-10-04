import argparse
import base64
import datetime
import time
import sys
import argparse
import logging
import sys
from uuid import UUID
from requests.utils import requote_uri

import requests
import ubirch
from ubirch_client import UbirchClient

log_levels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
}

parser = argparse.ArgumentParser(description='visitor counter')
parser.add_argument('-env', '--enviroment',
                    help="enviroment id, e.g. dev, demo, prod",
                    metavar="ENVID",
                    default="env")

parser.add_argument('-cid', '--counterid',
                    help="UUID of the virtuel counter device",
                    metavar="CID",
                    required=True)

parser.add_argument('-pw', '--password',
                    help="ubirch auth pathword of current counter device",
                    metavar="PWD",
                    required=True)

args = parser.parse_args()

counterId = args.counterid
password = args.password
env = args.enviroment.lower()

apiConfig = {
    "password": password,
    "keyService": "https://key.{}.ubirch.com/api/keyService/v1/pubkey/mpack".format(env),
    "niomon": "https://niomon.{}.ubirch.com/".format(env),
    "dataMsgPack": "https://data.{}.ubirch.com/v1/msgPack".format(env),
    "dataJson": "https://data.{}.ubirch.com/v1/json".format(env)
}

url = apiConfig["dataJson"]
passwordB64 = base64.encodebytes(bytes(password, "UTF-8")).decode("utf-8").rstrip('\n')

headers = {"X-Ubirch-Auth-Type": "ubirch",
           "X-Ubirch-Hardware-Id": counterId,
           "X-Ubirch-Credential": passwordB64,
           "Content-Type": "application/json"}

def lookupMac(mac):
    url = requote_uri("https://api.macvendors.com/{}".format(mac))
    r = requests.get(url)
    # just to avoid blacklisting
    time.sleep(1)
    if (r.status_code < 300):
        return r.text
    else:
        return "unknown"

keystore = ubirch.KeyStore(UUID(counterId).hex + ".jks", "demo-keystore")

ubirch = UbirchClient(UUID(counterId), keystore, apiConfig['keyService'], apiConfig['niomon'], headers)

while 1:
    try:
        line = sys.stdin.readline().rstrip('\n').rstrip('\r')
    except KeyboardInterrupt:
        break

    splitted = line.split(",")
    if ((len(splitted) == 7) and (splitted[0] != 'Station MAC')):
        mac = splitted[0].strip()
        manufacturer = mac[:8]
        firstTime = splitted[1].strip()
        lastTime = splitted[2].strip()
        power = int(splitted[3].strip())
        packetsCount = int(splitted[4].strip())
        BSSID = splitted[5].strip()
        probedESSIDs = splitted[6].strip()
        dataJson = {
            "uuid": counterId,
            "msg_type": 66,
            "timestamp": datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat(),
            # "timestamp": int(round(time.time())),
            "data": {
                "msg_type": 66,
                "mac": mac,
                "manId": manufacturer,
                "manName": lookupMac(mac),
                "firstTime": firstTime,
                "lastTime": lastTime,
                "power": power,
                "packetsCount": packetsCount,
                "BSSID": BSSID,
                "probedESSIDs": probedESSIDs
            }
        }

        print(dataJson)

        # r = requests.post(url,
        #                   headers=headers,
        #                   timeout=5,
        #                   json=dataJson
        #                   )

        if (r.status_code == 200):
            print("send data successfully")
            ubirch.send(dataJson)
        else:
            print("error: {}".format(r.status_code))
