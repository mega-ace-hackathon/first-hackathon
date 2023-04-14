import os

from algosdk.v2client import algod
from beaker import sandbox

DEFAULT_HOST = "localhost"


def algo_init(algod_address=None):
    if algod_address is None:
        algod_address = getNodeUrl(4001)
    # connect to network (for demo purposes, sandbox)
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)
    return algod_client


def getNodeUrl(port):
    host = os.environ.get("ALGOD_HOST", DEFAULT_HOST)
    return "http://%s:%d"%(host, port)


def getArgs():
    accounts = sandbox.get_accounts(getNodeUrl(4002))
    creator, receiver = accounts[0], accounts[1]
    return creator.address, creator.private_key, receiver.address, receiver.private_key
