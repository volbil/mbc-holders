from app.settings import get_settings
from datetime import datetime
import aiohttp
import json


async def make_request(endpoint: str, requests: list[dict] = []):
    async with aiohttp.ClientSession() as session:
        headers = {"content-type": "application/json;"}
        data = json.dumps(requests)

        try:
            async with session.post(endpoint, headers=headers, data=data) as r:
                return await r.json()
        except Exception:
            return None


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
