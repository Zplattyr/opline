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

engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10
)

def getAndResetUrls(engine):
    with engine.connect() as condata:
        res = condata.execute(text("select * from availables")).all()
    urls = [url for _, url in res]
    for url in urls:
        resetUrl(url, engine)


def resetUrl(url:str, engine):
    host = url.split('@')[1].split(':')[0]
    fullname = url.split('#')[1].split('-')
    name = fullname[-5] + '-' + fullname[-4] + '-' + fullname[-3] + '-' + fullname[-2] + '-' + fullname[-1]
    server = fullname[0] + '-' + fullname[1] + '-' + fullname[2]

    host, main_port, panel, username, password = getHostData(host, engine)

    # print(host, main_port, panel, username, password)
    onliners, inbounds = getOnliners(host, main_port, panel, username, password)
    if not onliners: onliners = []
    # print(inbounds)


    for indata in inbounds:
        remark = indata['remark']
        if remark != server:
            continue
        print(indata)
        clients = json.loads(indata['settings'])['clients']
        for client in clients:
            print(client['email'], name, onliners, server)
            if client['email'] == name and name not in onliners:
                id = indata['id']
                if server.find('trojan') != -1:
                    print(url)
                    pbk = json.loads(indata['streamSettings'])['realitySettings']['settings']['publicKey']
                    sid = json.loads(indata['streamSettings'])['realitySettings']['shortIds'][0]
                    key = addTrojan(host,main_port,indata['port'],panel,username,password,id, pbk, sid, server)
                    AddToAvailables(engine, key)
                    deleteTrojan(host, main_port, panel, username, password, id, client['password'])
                    DeleteFromAvailables(engine, url)


def DeleteFromAvailables(engine, url):
    while True:
        try:
            with engine.begin() as condata:
                condata.execute(text('delete from availables where "url" = \'' + url + '\''))
            break
        except:
            print('cantaddtoavailables')

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
        print(response.text)




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
    return key


def generate_base62_password(length=10):
    # Base62: 10 цифр + 26 строчных букв + 26 заглавных букв
    base62_chars = string.digits + string.ascii_letters
    # Генерация пароля случайным выбором символов из набора Base62
    password = ''.join(random.choice(base62_chars) for _ in range(length))
    return password

def getHostData(host, engine):
    with engine.connect() as conn:
        stmt = text('select * from hosts where "host" = \'' + host + '\'')
        res = conn.execute(stmt)
        host_info = res.fetchall()[0]

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
getAndResetUrls(engine)

