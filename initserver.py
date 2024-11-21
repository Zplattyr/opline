from resetUrls import getOnliners, addTrojan, addVless, AddToAvailables
from main import engine
import json

with open("login.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

    host = lines[0].strip()
    main_port = lines[1].strip()
    panel = lines[2].strip()
    username = lines[3].strip()
    password = lines[4].strip()
    count = int(lines[5].strip())
    proto = lines[6].strip()

    onliners, inbounds = getOnliners(host, main_port, panel, username, password)
    for indata in inbounds:
        remark = indata['remark']
        id = indata['id']
        if remark.find('trojan') != -1:
            pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
            sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
            for i in range(count):
                key = addTrojan(host,main_port,indata['port'],panel,username,password,id, pbk, sid, remark)
                AddToAvailables(engine, key)
        elif remark.find('vless') != -1:
            pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
            sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
            for i in range(count):
                key = addVless(host, main_port, indata['port'], panel, username, password, id, pbk, sid, remark)
                AddToAvailables(engine, key)


