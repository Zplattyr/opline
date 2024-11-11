import asyncio
import random
import time
from sqlalchemy import URL, create_engine, text
import requests
import json
import uuid
from config import settings
import base64
import random
import string
import os


async def getAndResetUrls(engine, mutex, stop_event):
    while True:
        async with mutex:
            with engine.connect() as condata:
                res = condata.execute(text("select * from availables")).all()
        urls = [url for _, url in res]
        for url in urls:
            await resetUrl(url, engine, mutex, stop_event)
            print("deleted url:", url[0:30])
        await asyncio.sleep(240)
        print('1 minute before reset urls')
        await asyncio.sleep(60)


async def resetUrl(url:str, engine, mutex, stop_event):
    try:
        host = url.split('@')[1].split(':')[0]
        fullname = url.split('#')[1].split('-')
        name = fullname[-5] + '-' + fullname[-4] + '-' + fullname[-3] + '-' + fullname[-2] + '-' + fullname[-1]
        server = fullname[0] + '-' + fullname[1] + '-' + fullname[2]
    except:
        return

    async with mutex:
        host, main_port, panel, username, password = getHostData(host, engine)

    # print(host, main_port, panel, username, password)
    onliners, inbounds = getOnliners(host, main_port, panel, username, password)
    if not onliners: onliners = []
    # print(inbounds)


    for indata in inbounds:
        remark = indata['remark']
        if remark != server:
            continue
        # print(indata)
        clients = json.loads(indata['settings'])['clients']
        for client in clients:
            # print(client['email'], name, onliners, server)
            if client['email'] == name and name not in onliners:
                id = indata['id']
                if server.find('trojan') != -1:
                    # print(url)
                    pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
                    sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
                    key = addTrojan(host,main_port,indata['port'],panel,username,password,id, pbk, sid, server)
                    stop_event.set()
                    async with mutex:
                        AddToAvailables(engine, key)
                        DeleteFromAvailables(engine, url)
                    stop_event.clear()
                    deleteTrojan(host, main_port, panel, username, password, id, client['password'])
                elif server.find('vless') != -1:
                    # print(url)
                    pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
                    sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
                    key = addVless(host, main_port, indata['port'], panel, username, password, id, pbk, sid, server)
                    stop_event.set()
                    async with mutex:
                        AddToAvailables(engine, key)
                        DeleteFromAvailables(engine, url)
                    stop_event.clear()
                    deleteVless(host, main_port, panel, username, password, id, client['id'])
                elif server.find('shadowsocks') != -1:
                    # print(indata)
                    security = json.loads(indata['settings'])['method']
                    host_pwd = json.loads(indata['settings'])['password']
                    key = addSS(host, main_port, indata['port'], panel, username, password, id, security, host_pwd, server)
                    # print(key)
                    stop_event.set()
                    async with mutex:
                        AddToAvailables(engine, key)
                        DeleteFromAvailables(engine, url)
                    stop_event.clear()
                    deleteSS(host, main_port, panel, username, password, id, client['email'])


def DeleteFromAvailables(engine, url):
    while True:
        try:
            with engine.begin() as condata:
                condata.execute(text('delete from availables where "url" = \'' + url + '\''))
            break
        except:
            print('cantdeletefromavailables')

def AddToAvailables(engine, url):
    while True:
        try:
            with engine.begin() as condata:
                condata.execute(text('insert into availables (url) values (\'' + url + '\')'))
            break
        except:
            print('cantaddtoavailables')

def deleteTrojan(host,main_port,panel,username,password,id,pwd):
        session = requests.session()
        url = f"http://{host}:{main_port}/{panel}/login"
        data = {
            'username': username,
            'password': password
        }
        response = session.post(url, data=data)
        url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/" + str(id) + "/delClient/" + str(pwd)
        payload = {}
        headers = {
            'Accept': 'application/json'
        }
        response = session.request("POST", url, headers=headers, data=payload)
        # print(response.text)



def addVless(host, main_port, port, panel, username, password, id, pbk, sid, server):
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/addClient/"
    headers = {
        'Accept': 'application/json'
    }
    client_data = {
        "id": id,
        "settings": json.dumps({
            "clients": [{
                "id": str(uuid.uuid1()),
                "alterId": 90,
                "flow": "xtls-rprx-vision",
                "email": str(uuid.uuid1()),
                "limitIp": 1,
                "totalGB": 0,
                "expiryTime": 0,
                "enable": True,
                "tgId": "",
                "subId": str(uuid.uuid1())
            }]
        })
    }
    key = f"vless://{json.loads(client_data['settings'])['clients'][0]['id']}@{host}:{port}?type=tcp&security=reality&pbk={pbk}&fp=random&sni=yahoo.com&sid={sid}&spx=%2F&flow=xtls-rprx-vision#{server}-{json.loads(client_data['settings'])['clients'][0]['email']}"
    response = session.request("POST", url, headers=headers, data=client_data)
    # print(response.text)
    return key

def deleteVless(host,main_port,panel,username,password,id,client_id):
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    old_client_id = client_id
    # print(old_client_id, id)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/" + str(id) + "/delClient/" + str(old_client_id)
    payload = {}
    headers = {
        'Accept': 'application/json'
    }
    response = session.request("POST", url, headers=headers, data=payload)

    # print(response.text)

def deleteSS(host,main_port,panel,username,password,id,pwd):
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/" + str(id) + "/delClient/" + str(pwd)
    payload = {}
    headers = {
        'Accept': 'application/json'
    }
    response = session.request("POST", url, headers=headers, data=payload)

    # print(response.text)

def addSS(host, main_port, port, panel, username, password, id, security, host_pwd, server):
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/addClient/"
    headers = {
        'Accept': 'application/json'
    }
    client_data = {
        "id": id,
        "settings": json.dumps({
            "clients": [{
      "method": "",
      "password": generate_random_base64_password(),
      "email": str(uuid.uuid1()),
      "limitIp": 1,
      "totalGB": 0,
      "expiryTime": 0,
      "enable": True,
      "tgId": "",
      "subId": str(uuid.uuid1()),
      "reset": 0
    }]
        })
    }
    a = f"{security}:{host_pwd}:{json.loads(client_data['settings'])['clients'][0]['password']}"
    a = base64.b64encode(a.encode()).decode()
    a = a.split('=')[0]
    key = f"ss://{a}@{host}:{port}?type=tcp#{server}-{json.loads(client_data['settings'])['clients'][0]['email']}"
    response = session.request("POST", url, headers=headers, data=client_data)
    # print(response)
    return key

def generate_random_base64_password(length=32):
    # Генерируем случайные байты заданной длины
    random_bytes = os.urandom(length)
    # Кодируем в Base64
    base64_password = base64.b64encode(random_bytes).decode()
    return base64_password

def addTrojan(host, main_port, port, panel, username, password, id, pbk, sid, server):
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/addClient/"
    headers = {
        'Accept': 'application/json'
    }
    client_data = {
        "id": id,
        "settings": json.dumps({
            "clients": [{
      "password": generate_base62_password(),
      "email": str(uuid.uuid1()),
      "limitIp": 1,
      "totalGB": 0,
      "expiryTime": 0,
      "enable": True,
      "tgId": "",
      "subId": str(uuid.uuid1()),
      "reset": 0
    }]
        })
    }
    key = f"trojan://{json.loads(client_data['settings'])['clients'][0]['password']}@{host}:{port}?type=tcp&security=reality&pbk={pbk}&fp=random&sni=yahoo.com&sid={sid}&spx=%2F#{server}-{json.loads(client_data['settings'])['clients'][0]['email']}"
    response = session.request("POST", url, headers=headers, data=client_data)
    # print(response)
    return key


def generate_base62_password(length=10):
    # Base62: 10 цифр + 26 строчных букв + 26 заглавных букв
    base62_chars = string.digits + string.ascii_letters
    # Генерация пароля случайным выбором символов из набора Base62
    password = ''.join(random.choice(base62_chars) for _ in range(length))
    return password

def getHostData(host, engine):
    while True:
        try:
            with engine.connect() as conn:
                stmt = text('select * from hosts where "host" = \'' + host + '\'')
                res = conn.execute(stmt)
                host_info = res.fetchall()[0]
            break
        except:
            print('cantgethostdata')

    host = host_info[1]
    main_port = host_info[2]
    panel = host_info[3]
    username = host_info[4]
    password = host_info[5]

    return host, main_port, panel, username, password

def getOnliners(host, main_port, panel, username, password):
    host = host
    main_port = main_port
    panel = panel
    username = username
    password = password
    session = requests.session()
    url = f"http://{host}:{main_port}/{panel}/login"
    data = {
        'username': username,
        'password': password
    }
    response = session.post(url, data=data)
    # print(response.text)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/onlines"
    response = session.request("POST", url)
    # print(response.text)

    onliners = response.json()['obj']

    url2 = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/list"
    list_inbounds = session.get(url2)
    return onliners, list_inbounds.json()['obj']

# encoded_str = "MjAyMi1ibGFrZTMtYWVzLTI1Ni1nY206NVIyc2VDQmxRWkcyVWtRMGVWS3FtTjY0VXFVdVlBZFh5NGwzc1Z2REFFWT06amNOeHFBUmgramN2cVptMDE0dmNYT0o3M3VwNlh3YmNuTis2L3JlUEFlcz0"
#
# missing_padding = len(encoded_str) % 4
# if missing_padding:
#     encoded_str += '=' * (4 - missing_padding)
#
# # Декодирование строки
# decoded_bytes = base64.b64decode(encoded_str)
# decoded_str = decoded_bytes.decode('utf-8')  # Если строка в UTF-8
# # 2022-blake3-aes-256-gcm:5R2seCBlQZG2UkQ0eVKqmN64UqUuYAdXy4l3sVvDAEY=:jcNxqARh+jcvqZm014vcXOJ73up6XwbcnN+6/rePAes=
# print(decoded_str)
# getAndResetUrls(engine)


# security = '2022-blake3-aes-256-gcm'
# host_pwd = "gJLgl5l1Ze4M7DTY7EpmlSG1aT8f1IZVUC76HDOm0BU="
# client_pwd = "NYW4btPNcbAJ4aKnsch9/AMSWxscnRGNvgYQReq9vNw="
#
# a = f"{security}:{host_pwd}:{client_pwd}"
# a = str(base64.b64encode(a.encode()))
# a = a.split('=')[0]
# print(a)
# 'MjAyMi1ibGFrZTMtYWVzLTI1Ni1nY206Z0pMZ2w1bDFaZTRNN0RUWTdFcG1sU0cxYVQ4ZjFJWlZVQzc2SERPbTBCVT06TllXNGJ0UE5jYkFKNGFLbnNjaDkvQU1TV3hzY25SR052Z1lRUmVxOXZOdz0'
# 'MjAyMi1ibGFrZTMtYWVzLTI1Ni1nY206Z0pMZ2w1bDFaZTRNN0RUWTdFcG1sU0cxYVQ4ZjFJWlZVQzc2SERPbTBCVT06TllXNGJ0UE5jYkFKNGFLbnNjaDkvQU1TV3hzY25SR052Z1lRUmVxOXZOdz0@'
