from app.sync import sync_chain
import asyncio


if __name__ == "__main__":
    asyncio.run(sync_chain())
