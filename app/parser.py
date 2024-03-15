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


def parse_transaction(tx_data):
    coinbase = False
    outputs = []
    inputs = []

    for vin_index, vin in enumerate(tx_data["vin"]):
        if "coinbase" in vin:
            inputs.append(
                {
                    "script_sig_hex": vin["coinbase"],
                    "script_sig_type": "coinbase",
                    "sequence": vin["sequence"],
                    "output_index": None,
                    "output_txid": None,
                    "index": vin_index,
                    "witness": [],
                }
            )

        else:
            witness = []

            if "txinwitness" in vin:
                for witness_index, witness_data in enumerate(
                    vin["txinwitness"]
                ):
                    witness.append(
                        {"index": witness_index, "script": witness_data}
                    )

            inputs.append(
                {
                    "sequence": vin["sequence"],
                    "script_sig_hex": vin["scriptSig"]["hex"],
                    "script_sig_asm": vin["scriptSig"]["asm"],
                    "output_index": vin["vout"],
                    "output_txid": vin["txid"],
                    "script_sig_type": None,
                    "index": vin_index,
                    "witness": witness,
                }
            )

    for vout_index, vout in enumerate(tx_data["vout"]):
        address = None
        req_sigs = 0

        # Older version
        if "addresses" in vout["scriptPubKey"]:
            address = vout["scriptPubKey"]["addresses"][0]

        # Newer versions
        if "address" in vout["scriptPubKey"]:
            address = vout["scriptPubKey"]["address"]

        if "reqSigs" in vout["scriptPubKey"]:
            req_sigs = vout["scriptPubKey"]["reqSigs"]

        outputs.append(
            {
                "value": vout["value"],
                "script_type": vout["scriptPubKey"]["type"],
                "script_hex": vout["scriptPubKey"]["hex"],
                "script_asm": vout["scriptPubKey"]["asm"],
                "address": address,
                "req_sigs": req_sigs,
                "index": vout_index,
            }
        )

    return {
        "created": datetime.fromtimestamp(tx_data["time"]),
        "confirmations": tx_data["confirmations"],
        "lock_time": tx_data["locktime"],
        "version": tx_data["version"],
        "timestamp": tx_data["time"],
        "weight": tx_data["weight"],
        "hash": tx_data["txid"],
        "size": tx_data["size"],
        "block_height": height,
        "hex": tx_data["hex"],
        "coinbase": coinbase,
        "outputs": outputs,
        "inputs": inputs,
    }


def parse_block(block_data):
    return {
        "created": datetime.fromtimestamp(block_data["time"]),
        "version_hex": block_data["versionHex"],
        "merkle_root": block_data["merkleroot"],
        "difficulty": block_data["difficulty"],
        "chainwork": block_data["chainwork"],
        "transactions": block_data["tx"],
        "version": block_data["version"],
        "timestamp": block_data["time"],
        "height": block_data["height"],
        "weight": block_data["weight"],
        "nonce": block_data["nonce"],
        "bits": block_data["bits"],
        "hash": block_data["hash"],
        "size": block_data["size"],
        "prev_hash": (
            block_data["previousblockhash"]
            if "previousblockhash" in block_data
            else None
        ),
    }
