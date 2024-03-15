from sqlalchemy import select, update, desc, func
from app.parser import parse_block, make_request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from app.settings import get_settings
from datetime import datetime
from pprint import pprint
import asyncio

from app.models import (
    Transaction,
    Output,
    Input,
    Block,
)


async def process_block(session: AsyncSession, data: dict):
    block = Block(
        **{
            "prev_blockhash": data.get("previousblockhash", None),
            "created": datetime.fromtimestamp(data["time"]),
            "transactions": data["tx"],
            "blockhash": data["hash"],
            "timestamp": data["time"],
            "height": data["height"],
        }
    )

    # print(f"Processed block #{block.height} ({block.blockhash})")

    session.add(block)


async def process_transaction(session: AsyncSession, data: dict):
    transaction = Transaction(
        **{
            "created": datetime.fromtimestamp(data["time"]),
            "blockhash": data["blockhash"],
            "timestamp": data["time"],
            "txid": data["txid"],
        }
    )

    session.add(transaction)

    # print(f"Processed transaction ({transaction.txid})")

    for vin in data["vin"]:
        if "coinbase" in vin:
            continue

        session.add(
            Input(
                **{
                    "shortcut": vin["txid"] + ":" + str(vin["vout"]),
                    "blockhash": data["blockhash"],
                    "index": vin["vout"],
                    "txid": vin["txid"],
                }
            )
        )

    for vout in data["vout"]:
        if vout["value"] == 0:
            continue

        session.add(
            Output(
                **{
                    "shortcut": data["txid"] + ":" + str(vout["n"]),
                    "address": vout["scriptPubKey"]["address"],
                    "blockhash": data["blockhash"],
                    "amount": vout["value"],
                    "txid": data["txid"],
                    "index": vout["n"],
                    "spent": False,
                }
            )
        )


async def update_spent(
    session: AsyncSession, start_height: int, end_height: int
):
    blockhashes = await session.scalars(
        select(Block.blockhash).filter(
            Block.height >= start_height, Block.height <= end_height
        )
    )

    outputs = await session.scalars(
        select(Output.shortcut).filter(Output.blockhash.in_(blockhashes))
    )

    inputs = await session.scalars(
        select(Input.shortcut).filter(Input.shortcut.in_(outputs))
    )

    await session.execute(
        update(Output).filter(Output.shortcut.in_(inputs)).values(spent=True)
    )


async def recalculate_balances(
    session: AsyncSession, start_height: int, end_height: int
):
    # blockhashes = await session.scalars(
    #     select(Block.blockhash).filter(
    #         Block.height >= start_height, Block.height <= end_height
    #     )
    # )

    test_data = await session.execute(
        select(func.sum(Output.amount), Output.address).group_by(Output.address)
    )

    pprint(test_data.all())


async def test():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    step = 100

    async with sessionmanager.session() as session:
        blockchain_height = await make_request(
            settings.backend.node,
            [{"id": "info", "method": "getblockchaininfo", "params": []}],
        )

        latest_height_blockchain = blockchain_height[0]["result"]["blocks"]

        latest_height_database = await session.scalar(
            select(Block.height).order_by(desc(Block.height))
        )

        start_height = latest_height_database + 1

        while True:
            end_height = start_height + step

            if end_height > latest_height_blockchain:
                end_height = latest_height_blockchain

            print(f"Getting blocks ({start_height} - {end_height})")

            block_hashes_result = await make_request(
                settings.backend.node,
                [
                    {
                        "id": f"blockhash-#{height}",
                        "method": "getblockhash",
                        "params": [height],
                    }
                    for height in range(start_height, end_height + 1)
                ],
            )

            blocks_result = await make_request(
                settings.backend.node,
                [
                    {
                        "id": "block-" + result["result"],
                        "method": "getblock",
                        "params": [result["result"]],
                    }
                    for result in block_hashes_result
                ],
            )

            # print("Getting transactions")

            transactions_result = await make_request(
                settings.backend.node,
                [
                    {
                        "id": f"tx-{txid}",
                        "method": "getrawtransaction",
                        "params": [txid, True],
                    }
                    for block in blocks_result
                    for txid in block["result"]["tx"]
                ],
            )

            # print("Processing blocks")

            for data in blocks_result:
                await process_block(session, data["result"])

            # print("Processing transactions")

            for data in transactions_result:
                await process_transaction(session, data["result"])

            await session.commit()

            # await update_spent(session, start_height, end_height)
            # await session.commit()

            # await recalculate_balances(session, start_height, end_height)
            # await session.commit()

            start_height += 100

            if start_height > latest_height_blockchain:
                break

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(test())
