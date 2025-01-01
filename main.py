import time

from sqlalchemy import create_engine, text
from config import settings
from sqlalchemy import MetaData
from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
import asyncio
from getOnliners import getCountOnliners
from resetUrls import getAndResetUrls
from getOnliners import isUrlOnline
from data import onlinerskey, onlinerspass
from sqlalchemy.ext.asyncio import create_async_engine


mutex = asyncio.Lock()

class Passcode(BaseModel):
    passcode: str
    protocol: str
    country: str
    login: bool

metadata = MetaData()

engine = create_async_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

app = FastAPI()

MAX_ON_SERVER = 10
MAX_DEVICES = 2
stop_event = asyncio.Event()

@app.post("/get_key")
async def get_key(pasco: Passcode):
    if not pasco.login:
        print(pasco, "-4")
        async with engine.connect() as condata:
            print(pasco, "-3")
            res = (await condata.execute(text("select * from passcodes"))).fetchall()
            query = pasco
            passcodes = [passcode for passcode, date in res]
            dates = [date for passcode, date in res]
            pasco = pasco.passcode
            if len(pasco) > 10:
                return "!INVALID "
            res2 = (await condata.execute(text('select * from users_passcodes where "passcode" = \'' + pasco + '\''))).fetchall()
            if pasco in passcodes:
                print(pasco, "1")
                passdate = datetime.strptime(dates[passcodes.index(pasco)], "%Y-%m-%d")
                today = datetime.today()
                if pasco in onlinerspass:
                    if await check_count_online(pasco) >= MAX_DEVICES:
                        return "!WAIT "
                if passdate >= today:
                    print(pasco, "2")
                    if stop_event.is_set():
                        await stop_event.wait()
                    res = (await condata.execute(text("select * from availables"))).fetchall()
                    keys:list[str] = [key for _, key in res]
                    for key in keys:
                        print(pasco, "3")
                        if (query.country and key.find(query.country) == -1):
                            print(pasco, "4")
                            continue
                        if (query.protocol and key.find(query.protocol) == -1):
                            print(pasco, "5")
                            continue
                        count_onliners = 0
                        if(not query.login):
                            print(pasco, "6")
                            try:
                                count_onliners = getCountOnliners(key, engine)
                            except:
                                continue
                        if(count_onliners > MAX_ON_SERVER):
                            print(pasco, "7")
                            continue
                        try:
                            print(pasco, "8")
                            if not await isUrlOnline(engine, key):
                                print(pasco, "9")
                                if key in onlinerskey and time.time() - onlinerskey[key] < 1800:
                                    print(pasco, "10")
                                    continue
                                if query.passcode not in onlinerspass:
                                    print(pasco, "11")
                                    onlinerspass[query.passcode] = [1, time.time()]
                                else:
                                    print(pasco, "12")
                                    onlinerspass[query.passcode][0] += 1
                                    onlinerspass[query.passcode][1] = time.time()
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
        async with engine.connect() as condata:
            res = (await condata.execute(text("select * from passcodes"))).fetchall()
            passcodes = [passcode for passcode, date in res]
            dates = [date for passcode, date in res]
            pasco = pasco.passcode
            if len(pasco) > 10:
                return "!INVALID "
            res2 = (await condata.execute(text('select * from users_passcodes where "passcode" = \'' + pasco + '\''))).fetchall()
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


async def check_count_online(passcode):
    if passcode in onlinerspass:
        start_value = onlinerspass[passcode][0]
        await asyncio.sleep(5)
        end_value = onlinerspass[passcode][0]
        return end_value - start_value
    else:
        return 0


@app.post("/onlinepass")
async def is_online(pasco: Passcode):
    if pasco.passcode not in onlinerspass:
        onlinerspass[pasco.passcode] = [1, time.time()]
    else:
        onlinerspass[pasco.passcode][0] += 1
        onlinerspass[pasco.passcode][1] = time.time()

@app.post("/onlinekey")
async def is_online(pasco: Passcode):
    # print('received', pasco.passcode)
    onlinerskey[pasco.passcode] = time.time()


async def print_clients():
    while True:
        print(onlinerspass)
        print("main", onlinerskey)
        await asyncio.sleep(30)

async def delete_online_keys():
    while True:
        keys_to_pop = []
        for key in onlinerskey.keys():
            if time.time() - onlinerskey[key] > 3600:
                keys_to_pop.append(key)
        for key in keys_to_pop:
            onlinerskey.pop(key)
        await asyncio.sleep(3600)

@app.on_event("startup")
async def on_startup():
    # background_tasks.add_task(print_clients)
    # background_tasks.add_task(delete_online_keys)
    # background_tasks.add_task(getAndResetUrls, engine,stop_event)
    asyncio.create_task(print_clients())
    asyncio.create_task(delete_online_keys())
    asyncio.create_task(getAndResetUrls(engine, stop_event))
