import socket
import threading
import time

from sqlalchemy import URL, create_engine, text
from config import settings
from sqlalchemy import types
from sqlalchemy import Table, Column, Integer, String, MetaData
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
import asyncio
from getOnliners import getCountOnliners
from resetUrls import getAndResetUrls
from getOnliners import isUrlOnline


mutex = asyncio.Lock()

class Passcode(BaseModel):
    passcode: str
    protocol: str
    country: str
    login: bool

metadata = MetaData()

engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10
)

app = FastAPI()
onlinerspass = {}
onlinerskey:dict = {}
MAX_ON_SERVER = 10
MAX_DEVICES = 1
stop_event = asyncio.Event()

@app.post("/get_key")
async def get_key(pasco: Passcode):
    if not pasco.login:
        with engine.connect() as condata:
            res = condata.execute(text("select * from passcodes")).all()
            query = pasco
            passcodes = [passcode for passcode, date in res]
            dates = [date for passcode, date in res]
            pasco = pasco.passcode
            if len(pasco) > 10:
                return "!INVALID "
            res2 = condata.execute(text('select * from users_passcodes where "passcode" = \'' + pasco + '\'')).all()
            print("Passcode: ", pasco)
            print("SQL: ", res2)
            if pasco in passcodes:
                passdate = datetime.strptime(dates[passcodes.index(pasco)], "%Y-%m-%d")
                today = datetime.today()
                if pasco in onlinerspass:
                    if onlinerspass[pasco][0] > MAX_DEVICES:
                        return "!WAIT "
                if passdate >= today:
                    if stop_event.is_set():
                        await stop_event.wait()
                    async with mutex:
                        res = condata.execute(text("select * from availables")).all()
                    keys:list[str] = [key for _, key in res]
                    for key in keys:
                        if (query.country and key.find(query.country) == -1):
                            continue
                        if (query.protocol and key.find(query.protocol) == -1):
                            continue
                        count_onliners = 0
                        if(not query.login):
                            try:
                                count_onliners = getCountOnliners(key, engine)
                            except:
                                continue
                        print("Count: ", count_onliners)
                        if(count_onliners > MAX_ON_SERVER):
                            continue
                        try:
                            if not await isUrlOnline(engine, key, mutex):
                                print(key)
                                async with mutex:
                                    if key in onlinerskey and time.time() - onlinerskey[key] < 10:
                                        continue
                                    if query.passcode not in onlinerspass:
                                        onlinerspass[query.passcode] = [1, time.time()]
                                    else:
                                        if time.time() - onlinerspass[query.passcode][1] > 5:
                                            onlinerspass[query.passcode][0] = 1
                                            onlinerspass[query.passcode][1] = time.time()
                                        else:
                                            onlinerspass[query.passcode][0] += 1
                                return str(key) + ' ' + res2[0][0]
                            else:
                                continue
                        except:
                            print('nouser')
                            return "!INVLAID "
                else:
                    print('dateexpired')
                    return "!INVALID "
            else:
                print('notinpasscodes')
                return "!INVALID "
    else:
        with engine.connect() as condata:
            res = condata.execute(text("select * from passcodes")).all()
            query = pasco
            passcodes = [passcode for passcode, date in res]
            dates = [date for passcode, date in res]
            pasco = pasco.passcode
            if len(pasco) > 10:
                return "!INVALID "
            res2 = condata.execute(text('select * from users_passcodes where "passcode" = \'' + pasco + '\'')).all()
            print("Passcode: ", pasco)
            print("SQL: ", res2)
            if pasco in passcodes:
                passdate = datetime.strptime(dates[passcodes.index(pasco)], "%Y-%m-%d")
                today = datetime.today()
                if passdate >= today:
                    return 'OK ' + res2[0][0]
                else:
                    print('dateexpired')
                    return "!INVALID "
            else:
                print('notinpasscodes')
                return "!INVALID "


@app.post("/onlinepass")
async def is_online(pasco: Passcode):
    async with mutex:
        if pasco.passcode not in onlinerspass: onlinerspass[pasco.passcode] = [1, time.time()]
        else:
            if time.time() - onlinerspass[pasco.passcode][1] > 5:
                onlinerspass[pasco.passcode][0] = 1
                onlinerspass[pasco.passcode][1] = time.time()
            else:
                onlinerspass[pasco.passcode][0] += 1

@app.post("/onlinekey")
async def is_online(pasco: Passcode):
    async with mutex:
        onlinerskey[pasco.passcode] = time.time()


async def print_clients():
    while True:
        async with mutex:
            print(onlinerspass)
            print(onlinerskey)
        await asyncio.sleep(30)

async def delete_online_keys():
    while True:
        keys_to_pop = []
        async with mutex:
            for key in onlinerskey.keys():
                if time.time() - onlinerskey[key] > 600:
                    keys_to_pop.append(key)
        for key in keys_to_pop:
            onlinerskey.pop(key)
        await asyncio.sleep(600)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(print_clients())
    asyncio.create_task(delete_online_keys())
    asyncio.create_task(getAndResetUrls(engine, mutex, stop_event, onlinerskey))