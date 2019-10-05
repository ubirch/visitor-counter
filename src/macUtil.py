from requests.utils import requote_uri
import requests
import time
import hashlib
import macDb
import binascii

unknown="unknown"

def init(dbPath):
    macDb.init(dbPath)

def getMacManufacturerId(mac):
    if(mac != None and len(mac) >8):
        return mac[:8]
    else:
        return None

def hashedMac(mac):
    if(mac != None and mac != ""):
        m = hashlib.sha256()
        m.update(str.encode(mac, encoding="UTF-8"))
        digest = m.digest()
        hashStr = binascii.b2a_base64(digest, newline=False)
        return hashStr.decode("UTF-8")
    else:
        return None


def lookupMacRequest(mac):
    url = requote_uri("https://api.macvendors.com/{}".format(mac))
    r = requests.get(url)
    # just to avoid blacklisting
    time.sleep(1)
    if (r.status_code < 300):
        return r.text
    else:
        return unknown

def lookupMac(mac):
    macId = getMacManufacturerId(mac)
    dbResult = macDb.getManufacturer(macId)
    if(dbResult == None):
        name = lookupMacRequest(mac)
        if(name != unknown):
            macDb.store(macId, name)
        return name
    else:
        print("cache hit")
        return dbResult
