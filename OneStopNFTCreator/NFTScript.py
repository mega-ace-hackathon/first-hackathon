import hashlib
import json

import algosdk
from algosdk.v2client import algod
from beaker import sandbox


def mintNFT(algod_client, creator_address, creator_private_key, asset_name, asset_unit_name):
    #...
    return 0  #your confirmed transaction's asset id should be returned instead


def transferNFT(algod_client, creator_address, creator_private_key, receiver_address, receiver_private_key, asset_id):
    pass