import argparse
import base64
import datetime
import logging
import requests
import sys
import ubirch

from uuid import UUID

from ubirch_client import UbirchClient

import macUtil

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
                    help="ubirch auth password of current counter device",
                    metavar="PWD",
                    required=True)

parser.add_argument("-d", "--debug",
                    help="enable debug logging level (info, warn, debug)",
                    metavar="LOGLEVEL",
                    default="info")

parser.add_argument("-db", "--databasepath",
                    help="db path to chache manufacturer locally",
                    metavar="DBPATH",
                    default="./macDb.json")

args = parser.parse_args()

counterId = args.counterid
password = args.password
env = args.enviroment.lower()
dbPath = args.databasepath

loglevel = args.debug.upper()
logging.basicConfig(format='%(asctime)s %(name)20.20s %(levelname)-8.8s %(message)s', level=loglevel)
logger = logging.getLogger("visitorCounter")

apiConfig = {
    "password": password,
    "keyService": "https://key.{}.ubirch.com/api/keyService/v1/pubkey".format(env),
    "niomon": "https://niomon.{}.ubirch.com/".format(env),
    "dataMsgPack": "https://data.{}.ubirch.com/v1/msgPack".format(env),
    "dataJson": "https://data.{}.ubirch.com/v1/json".format(env)
}

url = apiConfig["dataJson"]
passwordB64 = base64.b64encode(bytes(password, "UTF-8")).decode("ascii").rstrip('\n')
headers = {"X-Ubirch-Auth-Type": "ubirch",
           "X-Ubirch-Hardware-Id": counterId,
           "X-Ubirch-Credential": passwordB64,
           "Content-Type": "application/json"}
logger.info("current password: {}".format(password))
logger.info("current HTTP headers: {}".format(headers))

keystore = ubirch.KeyStore(UUID(counterId).hex + ".jks", "demo-keystore")

ubirch = UbirchClient(UUID(counterId), keystore, apiConfig['keyService'], apiConfig['niomon'], headers)

macUtil.init(dbPath)

while 1:
    try:
        line = sys.stdin.readline().rstrip('\n').rstrip('\r')
    except KeyboardInterrupt:
        break

    try:
        splitted = line.split(",")
        if ((len(splitted) == 7) and (splitted[0] != 'Station MAC')):
            mac = splitted[0].strip()
            manId = macUtil.getMacManufacturerId(mac)
            manName = macUtil.lookupMac(mac)
            firstTime = splitted[1].strip()
            lastTime = splitted[2].strip()
            power = int(splitted[3].strip())
            packetsCount = int(splitted[4].strip())
            BSSID = splitted[5].strip()
            probedESSIDs = splitted[6].strip()
            timestamp =datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            dataJson = {
                "uuid": counterId,
                "msg_type": 66,
                "timestamp": timestamp,
                # "timestamp": int(round(time.time())),
                "data": {
                    "msg_type": 66,
                    "mac": mac,
                    "macHashed": macUtil.hashedMac(mac),
                    "manId": manId,
                    "manName": manName,
                    "firstTime": firstTime,
                    "lastTime": lastTime,
                    "power": power,
                    "packetsCount": packetsCount,
                    "BSSID": BSSID,
                    "probedESSIDs": probedESSIDs
                }
            }

            logger.info(dataJson)

            r = requests.post(url,
                              headers=headers,
                              timeout=20,
                              json=dataJson
                              )

            if (r.status_code < 300):
                logger.info("send data to data service successfully")
                ubirch.send(dataJson)
            else:
                logger.error("could not send data to data service, got http status {} with error message {}".format(r.status_code,r.text))
    except:
        logger.error("could not prcess data: {}".format(line))
