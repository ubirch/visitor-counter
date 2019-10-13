import argparse
import base64
import datetime
import json
import logging
import sys
from uuid import UUID

import requests
import ubirch

import macUtil
from ubirch_client import UbirchClient

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

parser.add_argument("-log", "--loglevel",
                    help="setting logging level (info, warn, debug)",
                    metavar="LOGLEVEL",
                    default="info")

parser.add_argument("-db", "--databasepath",
                    help="db path to chache manufacturer locally",
                    metavar="DBPATH",
                    default="./macsDb.json")

parser.add_argument("-dry", "--dryrun",
                    help="set to true run without posting any data",
                    metavar="DRY",
                    default=False)

args = parser.parse_args()

counterId = args.counterid
password = args.password
env = args.enviroment.lower()
dbPath = args.databasepath

dryRun = args.dryrun

loglevel = args.loglevel.upper()
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


def processStations(splitted):
    mac = splitted[0].strip()
    if(mac.startswith(":")):
        logger.warning("got invalid MAC: {}".format(mac))
        return None
    else:
        manId = macUtil.getMacManufacturerId(mac)
        manName = macUtil.lookupMac(mac)
        firstTime = splitted[1].strip()
        lastTime = splitted[2].strip()
        power = int(splitted[3].strip())
        packetsCount = int(splitted[4].strip())
        BSSID = splitted[5].strip()
        probedESSIDs = splitted[:6].strip()
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        jsonData = {
            "uuid": counterId,
            "msg_type": 66,
            "timestamp": timestamp,
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
        return jsonData


def processBssids(splitted):
    bssid = splitted[0].strip()
    first_time_seen = splitted[1].strip()
    last_time_seen = splitted[2].strip()
    channel = int(splitted[3].strip())
    speed = int(splitted[4].strip())
    privacy = splitted[5].strip()
    cipher = splitted[6].strip()
    authentication = splitted[7].strip()
    power = int(splitted[8].strip())
    beacons = int(splitted[9].strip())
    iv = int(splitted[10].strip())
    lan_ip = splitted[11].strip()
    id_length = int(splitted[12].strip())
    essid = splitted[13].strip()
    key = splitted[14].strip()

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    jsonData = {
        "uuid": counterId,
        "msg_type": 67,
        "timestamp": timestamp,
        "data": {
            "msg_type": 67,
            "BSSID": bssid,
            "first_time_seen": first_time_seen,
            "last_time_seen": last_time_seen,
            "channel": channel,
            "speed": speed,
            "privacy": privacy,
            "cipher": cipher,
            "authentication": authentication,
            "power": power,
            "beacons": beacons,
            "iv": iv,
            "lan_ip": lan_ip,
            "id_length": id_length,
            "essid": essid,
            "Key": key
        }
    }
    return jsonData


def storeProbedEssids(counterId, probedEssids):
    splitted = probedEssids.split("'")
    for pEssid in splitted:
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        jsonData = {
            "uuid": counterId,
            "msg_type": 68,
            "timestamp": timestamp,
            "data": {
                "msg_type": 68,
                "probedEssid": pEssid.strip()
            }
        }
        postJsonData(jsonData)


def postJsonData(jsonData):
    global headers
    logger.info(jsonData)

    r = requests.post(url,
                      headers=headers,
                      timeout=20,
                      json=jsonData
                      )

    if (r.status_code < 300):
        logger.info("send data to data service successfully")
        ubirch.send(jsonData)
    else:
        logger.error("could not send data to data service, got http status {} with error message {}".format(
            r.status_code, r.text))


def filterLine(line):
    filteredLine = ""
    for c in line:
        if (c >= ' ' and c <= '~'):
            filteredLine = filteredLine + c
    return filteredLine


while 1:
    try:
        line = filterLine(sys.stdin.readline())
        # .rstrip('\n').rstrip('\r')
        splitted = line.split(",")
        jsonData = None
        if ((len(splitted) != 15) and (splitted[0] != 'Station MAC')):
            jsonData = processStations(splitted)
            if (jsonData['data']['probedESSIDs'] > ""):
                probedEssids = jsonData['data']['probedESSIDs']
                logger.info("found probed SSIDs: {}".format(probedEssids))
                storeProbedEssids(counterId, probedEssids)
        elif ((len(splitted) == 15) and (splitted[0] != 'BSSID')):
            jsonData = processBssids(splitted)
        elif (line != None and line > ""):
            logger.error("invalid data: {}".format(line))

        if (jsonData != None and dryRun == False):
            postJsonData(jsonData)
        else:
            logger.debug("current jsonData: {}".format(json.dumps(jsonData, indent=4, sort_keys=True)))

    except KeyboardInterrupt:
        break
    except:
        logger.error("could not prcess data: {}".format(line))
