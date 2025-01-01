from sqlalchemy import insert,text,delete


def InsertUser(table, value):
    pass

def InsertUrl(engine, table, url):
    async with engine.connect() as conn:
        stmt = insert(table).values(
            [
                {"url": url}
            ]
        )
        conn.execute(stmt)
        conn.commit()

def InsertPasscode(engine, table, code, date):
    async with engine.connect() as conn:
        stmt = insert(table).values(
            [
                {"passcode": code, "expiry_date": date}
            ]
        )
        conn.execute(stmt)
        conn.commit()

def DeleteUrl(engine, table, url):
    async with engine.connect() as conn:
        stmt = delete(table).where(table.c.url == url)
        conn.execute(stmt)
        conn.commit()