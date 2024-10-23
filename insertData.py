from sqlalchemy import insert,text


def InsertUser(table, value):
    pass

def InsertUrl(engine, table, url):
    with engine.connect() as conn:
        stmt = insert(table).values(
            [
                {"url": url}
            ]
        )
        conn.execute(stmt)
        conn.commit()
