from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy import URL, create_engine, text, Date
from config import settings
from sqlalchemy import types
from sqlalchemy import Table, Column, Integer, String, MetaData

import insertData


metadata = MetaData()

passcodes = Table(
    "passcodes",
    metadata,
    Column("passcode", String, primary_key=True),
    Column("expiry_date", String)
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
    echo=True,
    pool_size=5,
    max_overflow=10
)

def create_tables():
    metadata.drop_all(engine)
    metadata.create_all(engine)




create_tables()
insertData.InsertUrl(engine, availables, 'vless://31aefed4-d979-4a72-ae72-eb8b618d7be4@185.70.199.184:3389?type=tcp&security=reality&pbk=0v3q7-B_aGeMZts8lmIeBAXHwnuwjikCgwoM6071PyU&fp=random&sni=yahoo.com&sid=ac&spx=%2F&flow=xtls-rprx-vision#comp2-3')
insertData.InsertUrl(engine, availables, 'vless://31aefefd4-d979-4a72-ae72-eb8b618d7be4@185.70.199.184:3389?type=tcp&security=reality&pbk=0v3q7-B_aGeMZts8lmIeBAXHwnuwjikCgwoM6071PyU&fp=random&sni=yahoo.com&sid=ac&spx=%2F&flow=xtls-rprx-vision#comp2-3')
insertData.InsertPasscode(engine, passcodes, 'pass', '2026-11-29')

with engine.connect() as conn:
    res = conn.execute(text("select * from availables"))
    print(f"{res.all()}")