import os
from sqlalchemy.engine import URL
from sqlalchemy import types, create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData
from .config import settings

postgress_url = settings.DATABASE_URL_psycopg

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

with engine.connect() as conn:
    metadata.create_all(engine)