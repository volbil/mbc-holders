from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from app.database import sessionmanager
from app.settings import get_settings
from app.parser import make_request
from datetime import datetime
from decimal import Decimal
from pprint import pprint
import asyncio

from app.models import (
    Transaction,
    Address,
    Output,
    Block,
    Input,
)


async def parse_outputs(transaction_data: dict):
    outputs = []

    for vout in transaction_data["vout"]:
        if "address" not in vout["scriptPubKey"]:
            continue

        outputs.append(
            {
                "shortcut": transaction_data["txid"] + ":" + str(vout["n"]),
                "blockhash": transaction_data["blockhash"],
                "address": vout["scriptPubKey"]["address"],
                "txid": transaction_data["txid"],
                "amount": vout["value"],
                "index": vout["n"],
                "spent": False,
            }
        )

    return outputs


async def parse_inputs(transaction_data: dict):
    inputs = []

    for vin in transaction_data["vin"]:
        if "coinbase" in vin:
            continue

        inputs.append(
            {
                "shortcut": vin["txid"] + ":" + str(vin["vout"]),
                "blockhash": transaction_data["blockhash"],
                "index": vin["vout"],
                "txid": vin["txid"],
            }
        )

    return inputs


async def parse_transactions(txids: list[str]):
    settings = get_settings()

    transactions_result = await make_request(
        settings.backend.node,
        [
            {
                "id": f"tx-{txid}",
                "method": "getrawtransaction",
                "params": [txid, True],
            }
            for txid in txids
        ],
    )

    transactions = []
    outputs = []
    inputs = []

    for transaction_result in transactions_result:
        transaction_data = transaction_result["result"]

        transactions.append(
            {
                "created": datetime.fromtimestamp(transaction_data["time"]),
                "blockhash": transaction_data["blockhash"],
                "timestamp": transaction_data["time"],
                "txid": transaction_data["txid"],
            }
        )

        outputs += await parse_outputs(transaction_data)

        inputs += await parse_inputs(transaction_data)

    input_transactions_result = await make_request(
        settings.backend.node,
        [
            {
                "id": f"input-tx-{txid}",
                "method": "getrawtransaction",
                "params": [txid, True],
            }
            for txid in list(set([vin["txid"] for vin in inputs]))
        ],
    )

    input_outputs = {}

    for transaction_result in input_transactions_result:
        transaction_data = transaction_result["result"]
        vin_vouts = await parse_outputs(transaction_data)

        for vout in vin_vouts:
            input_outputs[vout["shortcut"]] = vout

    movements = {}

    for output in outputs:
        if output["address"] not in movements:
            movements[output["address"]] = 0

        movements[output["address"]] += output["amount"]

    for input in inputs:
        input_output = input_outputs[input["shortcut"]]

        if input_output["address"] not in movements:
            movements[input_output["address"]] = 0

        movements[input_output["address"]] -= input_output["amount"]

    movements = {key: value for key, value in movements.items() if value != 0.0}

    return transactions, outputs, inputs, movements


async def parse_block(height: int):
    settings = get_settings()

    result = {}

    block_hash_result = await make_request(
        settings.backend.node,
        {
            "id": f"blockhash-#{height}",
            "method": "getblockhash",
            "params": [height],
        },
    )

    block_hash = block_hash_result["result"]

    block_data_result = await make_request(
        settings.backend.node,
        {
            "id": f"block-#{block_hash}",
            "method": "getblock",
            "params": [block_hash],
        },
    )

    block_data = block_data_result["result"]

    transactions, outputs, inputs, movements = await parse_transactions(
        block_data["tx"]
    )

    result["transactions"] = transactions
    result["outputs"] = outputs
    result["inputs"] = inputs
    result["block"] = {
        "prev_blockhash": block_data.get("previousblockhash", None),
        "created": datetime.fromtimestamp(block_data["time"]),
        "transactions": block_data["tx"],
        "blockhash": block_data["hash"],
        "timestamp": block_data["time"],
        "height": block_data["height"],
        "movements": movements,
    }

    return result


async def get_block_by_height(session: AsyncSession, height: int):
    return await session.scalar(select(Block).filter(Block.height == height))


async def process_block(session: AsyncSession, data: dict):
    # Add new block
    block = Block(**data["block"])
    session.add(block)

    # Add new outputs to the session
    session.add_all([Output(**output_data) for output_data in data["outputs"]])

    # Add new transactions to the session
    session.add_all(
        [
            Transaction(**transaction_data)
            for transaction_data in data["transactions"]
        ]
    )

    # Add new inputs to the session and collect spent output shortcuts
    input_shortcuts = []
    for input_data in data["inputs"]:
        input_shortcuts = [input_data["shortcut"]]
        session.add(Input(**input_data))

    # Mark outputs used in inputs as spent
    await session.execute(
        update(Output)
        .filter(Output.shortcut.in_(input_shortcuts))
        .values(spent=True)
    )

    # Get list of addresses involved in block transactions
    movement_addresses = list(data["block"]["movements"].keys())

    # Get existing addresses from database
    cache = await session.scalars(
        select(Address).filter(Address.address.in_(movement_addresses))
    )

    addresses_cache = {entry.address: entry for entry in cache}

    for raw_address in movement_addresses:
        if not (address := addresses_cache.get(raw_address)):
            address = Address(**{"address": raw_address, "balance": Decimal(0)})

        address.balance += Decimal(data["block"]["movements"][address.address])
        session.add(address)

    return block


async def sync_chain():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    async with sessionmanager.session() as session:
        latest = await session.scalar(
            select(Block).order_by(desc(Block.height))
        )

        if not latest:
            print("Adding genesis block to db")

            block_data = await parse_block(0)

            latest = await process_block(session, block_data)

            await session.commit()

        # while (
        #     latest.hash
        #     != (await client.make_request("getblockhash", [latest.height]))[
        #         "result"
        #     ]
        # ):
        #     print(f"Found reorg at height #{latest.height}")

        #     reorg_block = latest
        #     latest = await get_block_by_height(
        #         session, height=(latest.height - 1)
        #     )

        #     await session.delete(reorg_block)
        #     await session.commit()

        chain_data = await make_request(
            settings.backend.node,
            {"id": "info", "method": "getblockchaininfo", "params": []},
        )

        chain_blocks = chain_data["result"]["blocks"]
        display_log = (latest.height + 10) > chain_blocks

        for height in range(latest.height + 1, chain_blocks + 1):
            try:
                if display_log:
                    print(f"Processing block #{height}")
                else:
                    if height % 100 == 0:
                        print(f"Processing block #{height}")

                block_data = await parse_block(height)

                await process_block(session, block_data)

                await session.commit()

            except KeyboardInterrupt:
                print("Keyboard interrupt")
                break

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(sync_chain())
