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
import insertData


mutex = asyncio.Lock()

class Passcode(BaseModel):
    passcode: str

metadata = MetaData()

passcodes = Table(
    "passcodes",
    metadata,
    Column("passcode", String, primary_key=True),
    Column("expiry_date", types.Date)
)

availables = Table(
    "availables",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String)
)

uns = Table(
    "uns",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("url", String)
)

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("isAccepted", types.Boolean),
    Column("passcode", String)
)

engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=False,
    pool_size=5,
    max_overflow=10
)

app = FastAPI()
onliners = {}

@app.post("/get_key")
async def get_key(pasco: Passcode):
    async with mutex:
        with engine.connect() as condata:
            res = condata.execute(text("select * from passcodes")).all()
            passcodes = [passcode for passcode, date in res]
            dates = [date for passcode, date in res]
            pasco = pasco.passcode
            print(pasco)
            if pasco in  passcodes:
                passdate = datetime.strptime(dates[passcodes.index(pasco)], "%Y-%m-%d")
                today = datetime.today()
                if (passdate >= today):
                    res = condata.execute(text("select * from availables")).all()
                    keys = [key for _, key in res]
                    for key in keys:
                        if key not in onliners:
                            return key
                        else:
                            if time.time() - onliners[key] >= 30:
                                return key
                            else:
                                continue
                else:
                    return "!INVALID"
            else:
                return "!INVALID"




@app.post("/online")
async def is_online(pasco: Passcode):
    async with mutex:
        onliners[pasco.passcode] = time.time()
        print(onliners)

#
# HEADER = 64
# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER, PORT)
# FORMAT = 'utf-8'
#
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(ADDR)
#
# engine = create_engine(
#     url = settings.DATABASE_URL_psycopg,
#     echo=False,
#     pool_size=5,
#     max_overflow=10
# )
#
# avails1 = set()
# avails2 = set()
#
#
# my_mutex = threading.Lock()
# def handle_client(conn, addr):
#     print(f"[NEW CONNECTION] {addr} connected")
#
#     msg = conn.recv(1024).decode(FORMAT)
#     print(f"[{addr}] {msg}")
#     msg = msg.split()
#
#     if(msg[0] != '!PASSCODE'):
#         conn.close()
#
#     my_mutex.acquire()
#     with engine.connect() as condata:
#         res = condata.execute(text("select * from passcodes")).all()
#         passcodes = [passcode for passcode, date in res]
#         dates = [date for passcode, date in res]
#         print(passcodes)
#
#     if (msg[1] not in passcodes):
#         conn.send("!INVALID".encode('utf-8'))
#         conn.close()
#         my_mutex.release()
#         return
#
#     with engine.connect() as condata:
#         res = condata.execute(text("select * from availables"))
#         key = res.all()[0][1]
#         print(f"{key}")
#         insertData.InsertUrl(engine,uns,key)
#         insertData.DeleteUrl(engine,availables,key)
#
#     conn.send(key.encode('utf-8'))
#
#     my_mutex.release()
#     conn.close()
#
# def start():
#     server.listen()
#     while True:
#         conn, addr = server.accept()
#         thread = threading.Thread(target=handle_client, args=(conn, addr))
#         thread.start()
#         print(f"[ACTIVE CONNETCIONS] {threading.active_count() - 1}")
#
# print('starting...')
# start()