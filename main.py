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
onlinersid = {}

@app.post("/get_key")
async def get_key(pasco: Passcode):
    async with mutex:
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
            if pasco in  passcodes:
                passdate = datetime.strptime(dates[passcodes.index(pasco)], "%Y-%m-%d")
                today = datetime.today()
                if pasco in onlinersid:
                    if onlinersid[pasco] + 5 >= time.time():
                        return "!WAIT "
                if passdate >= today:
                    res = condata.execute(text("select * from availables")).all()
                    keys:list[str] = [key for _, key in res]
                    for key in keys:
                        if (query.country and key.find(query.country) == -1):
                            continue
                        if (query.protocol and key.find(query.protocol) == -1):
                            continue
                        count_onliners = 0
                        if(not query.login):
                            count_onliners = getCountOnliners(key, engine)
                        print("Count: ", count_onliners)
                        if(count_onliners > 3):
                            continue
                        try:
                            if key not in onlinerspass:
                                return str(key) + ' ' + res2[0][0]
                            else:
                                if time.time() - onlinerspass[key] >= 30:
                                    return str(key) + ' ' + res2[0][0]
                                else:
                                    continue
                        except:
                            return "!INVLAID "
                else:
                    return "!INVALID "
            else:
                return "!INVALID "


@app.post("/onlinepass")
async def is_online(pasco: Passcode):
    async with mutex:
        onlinerspass[pasco.passcode] = time.time()

@app.post("/onlineid")
async def is_online(pasco: Passcode):
    async with mutex:
        onlinersid[pasco.passcode] = time.time()


async def print_clients():
    while True:
        async with mutex:
            print(onlinersid)
            print(onlinerspass)
        await asyncio.sleep(10)

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(print_clients())