
app = FastAPI()



@app.post("/get_key")
async def get_key(pasco: Passcode):
    ...


@app.post("/onlinepass")
async def is_online(pasco: Passcode):
    ...

@app.post("/onlinekey")
async def is_online(pasco: Passcode):
    ...


async def print_clients():
    while True:
        ...

async def delete_online_keys():
    while True:
        ...

@app.on_event("startup")
async def on_startup():
    asyncio.create_task(print_clients())
    asyncio.create_task(delete_online_keys())
    asyncio.create_task(getAndResetUrls(engine, stop_event))
