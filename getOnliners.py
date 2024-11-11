import random
import time
from sqlalchemy import text
import requests
import json
import uuid
from resetUrls import getOnliners

def getCountOnliners(url, engine):
    host = url.split('@')[1].split(':')[0]

    host, main_port, panel, username, password = getHostData(host, engine)
    print(host, main_port, panel, username, password)

    return count_online(host, main_port, panel, username, password)

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

def count_online(host, main_port, panel, username, password):
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
    print(response.text)
    url = f"http://{host}:{main_port}/{panel}/panel/api/inbounds/onlines"
    response = session.request("POST", url)
    print(response.text)
    if (response.json()['obj']):
        count = len(response.json()['obj'])
    else:
        count = 0
    return count

async def isUrlOnline(engine, url, mutex):
    try:
        host = url.split('@')[1].split(':')[0]
        fullname = url.split('#')[1].split('-')
        name = fullname[-5] + '-' + fullname[-4] + '-' + fullname[-3] + '-' + fullname[-2] + '-' + fullname[-1]
        server = fullname[0] + '-' + fullname[1] + '-' + fullname[2]
    except:
        return
    async with mutex:
        host, main_port, panel, username, password = getHostData(host, engine)
    onliners, inbounds = getOnliners(host, main_port, panel, username, password)
    if not onliners: onliners = []
    return name in onliners