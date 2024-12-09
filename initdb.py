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
    Column("ref", String),
    Column("bonus", Integer)
)

refs = Table(
    "refs",
    metadata,
    Column("ref", String, primary_key=True),
    Column("id", String),
    Column("all_invited", Integer),
    Column("sincebuy_invited", Integer)
)

used_refs = Table(
    "used_refs",
    metadata,
    Column("id", String, primary_key=True),
    Column("ref", String)
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
    Column("country", String),
)

mobile_hosts = Table(
    "mobile_hosts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("host", String),
    Column("port", String),
    Column("panel", String),
    Column("username", String),
    Column("password", String),
    Column("count", Integer),
    Column("country", String),
)


engine = create_engine(
    url = settings.DATABASE_URL_psycopg,
    echo=True,
    pool_size=5,
    max_overflow=10
)

with engine.connect() as conn:
    metadata.create_all(engine)



