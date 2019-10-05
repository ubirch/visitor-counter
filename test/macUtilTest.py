import macUtil

macs = ["06:D6:AA:79:5C:AB",
        "D0:05:2A:A4:1D:16",
        "4A:67:51:56:E3:A5",
        "A0:E4:CB:25:A2:D5",
        "DE:9F:DB:3C:E9:6A",
        "98:DE:D0:5C:67:66",
        "46:67:51:48:F2:A9"]

macUtil.init("./macsdb.json")

for mac in macs:
    name = macUtil.lookupMac(mac)
    print(macUtil.hashedMac(mac))
    print(name)

