import hashlib
import json

import algosdk
from algosdk.v2client import algod
from beaker import sandbox

from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, wait_for_confirmation

import requests

PINATA_JWT = ""
UPLOAD_TO_PINATA = False
IPFS_FOLDER = "ipfs_folder"
IPFS_HASH = 'bafybeifoxvha7bknswmvhd7sedn26y5vx4js4oo65nixkmgkjnn2lcobau'


def mintNFT(algod_client, creator_address, creator_private_key, asset_name, asset_unit_name):
    name = asset_name
    image = "avatar.png"
    decimals = 0
    (meta_json, hash) = create_nft_metadata(name, image, decimals)
    ipfs_hash = IPFS_HASH
    if UPLOAD_TO_PINATA:
        ipfs_hash = upload_to_pinata(PINATA_JWT)

    # create nft txn
    params = algod_client.suggested_params()
    txn = AssetConfigTxn(
        sender=creator_address,
        sp=params,
        total=1,
        default_frozen=False,
        unit_name=asset_unit_name,
        asset_name=asset_name,
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        url=f"ipfs:://{ipfs_hash}/metadata.json#arc3",
        metadata_hash=hash,
        decimals=decimals
    )

    (txid, _) = sign_and_send_txn(algod_client, creator_private_key, txn)

    try:
        ptx = algod_client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
    except Exception as e:
        print(e)

    return asset_id  # your confirmed transaction's asset id should be returned instead


def transferNFT(algod_client, creator_address, creator_private_key, receiver_address, receiver_private_key, asset_id):
    # Opt-in
    optin(algod_client, asset_id, receiver_address, receiver_private_key)
    # transfert NFT
    transfer_nft(algod_client, receiver_address,
                 creator_address, creator_private_key, asset_id)
    return

# helpers


def upload_to_pinata(pinata_jwt):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    payload = {'pinataOptions': '{"cidVersion": 1}', }

    with open(f'./{IPFS_FOLDER}/avatar.png', 'rb') as avatar_file:
        with open(f'./{IPFS_FOLDER}/metadata.json', 'rb') as meta_file:
            files = [
                ('file', ('/mega-ace-nft/avatar.png', avatar_file,
                          'application/octet-stream')),
                ('file', ('/mega-ace-nft/metadata.json', meta_file,
                          'application/octet-stream')),
            ]
            headers = {'Authorization': f'Bearer {pinata_jwt}'}
            response = requests.request(
                "POST", url, headers=headers, data=payload, files=files)

    return json.loads(response.text)["IpfsHash"]


def create_nft_metadata(name, image, decimals):
    default_json = """
    {
    "name": "default",
    "image": "default.png",
    "decimals": 0
    }
    """
    meta = json.loads(default_json)
    meta['name'] = name
    meta['image'] = image
    meta['decimals'] = decimals
    meta_json = json.dumps(meta)
    with open(f'./{IPFS_FOLDER}/metadata.json', 'w') as outfile:
        json.dump(meta, outfile)

    h = hashlib.new("sha256")
    h.update(meta_json.encode("utf-8"))
    json_metadata_hash = h.digest()

    return (meta_json, json_metadata_hash)


def sign_and_send_txn(algod_client, signer_private_key, txn):
    stxn = txn.sign(signer_private_key)
    txid = algod_client.send_transaction(stxn)
    # Wait for the transaction to be confirmed
    confirmed_txn = wait_for_confirmation(algod_client, txid)
    return (txid, confirmed_txn)


def optin(algod_client, asset_id, receiver_address, receiver_private_key):
    params = algod_client.suggested_params()
    # reciever opt-in
    #
    account_info = algod_client.account_info(receiver_address)
    holding = False
    idx = 0
    for _ in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['asset-id'] == asset_id):
            holding = True
            break

    if not holding:
        optin_txn = AssetTransferTxn(
            sender=receiver_address,
            sp=params,
            receiver=receiver_address,
            amt=0,
            index=asset_id)
        sign_and_send_txn(algod_client, receiver_private_key, optin_txn)
    else:
        print("reciever already holds asset-id")


def transfer_nft(algod_client, receiver_address, creator_address, creator_private_key, asset_id):
    params = algod_client.suggested_params()
    txn_transfer = AssetTransferTxn(
        sender=creator_address,
        sp=params,
        receiver=receiver_address,
        amt=1,
        index=asset_id,
    )
    sign_and_send_txn(algod_client, creator_private_key, txn_transfer)
