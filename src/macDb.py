from tinydb import TinyDB, Query

db = None
macTable = None
macsQuery = None

def init(dbPath):
    global db, macTable, macsQuery
    db = TinyDB(dbPath)
    macTable = db.table('macs')
    macsQuery = Query()

def store(macId, name):
    res = get(macId)
    if(res == None):
        macTable.insert({'macId': macId, 'name': name})
    else:
        print("already stored {}".format(macId))

def get(macId):
    res = macTable.search(macsQuery.macId == macId)
    if (len(res) == 1):
        return res[0]
    else:
        return None

def getManufacturer(macId):
    res = get(macId)
    if(res != None):
        return res['name']
    else:
        return None

def close():
    db.close()
