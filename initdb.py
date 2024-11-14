import os
from sqlalchemy.engine import URL
from sqlalchemy import types, create_engine, text
from sqlalchemy import Table, Column, Integer, String, MetaData
from config import settings

postgress_url = settings.DATABASE_URL_psycopg

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

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("isAccepted", String),
)

users_passcodes = Table(
    "users_passcodes",
    metadata,
    Column("user", String),
    Column("passcode", String, primary_key=True),
)

promocodes = Table(
    "promocodes",
    metadata,
    Column("promocode", String, primary_key=True),
    Column("count", Integer),
    Column("limit", Integer)
)

users_promocodes = Table(
    "users_promocodes",
    metadata,
    Column("id", String),
    Column("promocode", String),
)

hosts = Table(
    "hosts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("host", String),
    Column("port", String),
    Column("panel", String),
    Column("username", String),
    Column("password", String),
    Column("count", Integer),
)


engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=True,
    pool_size=5,
    max_overflow=10
)

def UpdatePromocode(engine, count, promocode):
    while True:
        try:
            with engine.begin() as conn:
                stmt = text('update promocodes set "count" = ' + str(count) + ' where "promocode" = \'' + promocode +'\'')
                conn.execute(stmt)
            break
        except:
            print('cant updatepromocode')

def GetPromocode(engine, promocode):
    while True:
        try:
            with engine.connect() as conn:
                stmt = text('select * from promocodes where "promocode" = \'' + promocode + '\'')
                res = conn.execute(stmt)
                return res.fetchall()[0]
        except:
            print('cant getpromocde')

def AddToUsersPromocodes(engine, id, promocode):
    while True:
        try:
            with engine.begin() as condata:
                condata.execute(text('insert into users_promocodes (id, promocode) values (\'' + id + '\', \'' + promocode + '\')'))
            break
        except:
            print('cantaddtouserspromocodes')

def GetUsersPromocodes(engine, id):
    while True:
        try:
            with engine.connect() as conn:
                stmt = text('select * from users_promocodes where id = \'' + id + '\'')
                res = conn.execute(stmt)
                return res.fetchall()[0]
        except:
            print('cant getuserspromocodes')



with engine.connect() as conn:
    metadata.create_all(engine)

print(GetUsersPromocodes(engine, '12345'))


