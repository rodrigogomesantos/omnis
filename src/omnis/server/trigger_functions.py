from asyncio import sleep
async def pauseRequest(**kargs):
    print("Pause")
    print(kargs)
    await sleep(1)