import os
import sys
import unittest

from algosdk.v2client import algod
from beaker import sandbox

from NFTScript import mintNFT, transferNFT


desired_unit_name = "hc"
desired_asset_name = "HackaCoin"


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


class NFTTestBase(unittest.TestCase):
    algod_client = None
    asset_id = os.environ.get('ASSET_ID', None)

    @classmethod
    def log(cls, *args):
        print(' '.join(str(x) for x in args), file=sys.stderr)

    @classmethod
    def callTest(cls):
        cls.asset_id = mintNFT(cls.algod_client, cls.creator_address, cls.creator_private_key, desired_asset_name, desired_unit_name)
        transferNFT(cls.algod_client, *cls.args, cls.asset_id)
        return cls.asset_id

    @classmethod
    def setUpClass(cls) -> None:
        if cls.algod_client is None:
            cls.algod_client = algo_init(getNodeUrl(4001))
        cls.args = cls.creator_address, cls.creator_private_key, cls.receiver_address, cls.receiver_private_key = getArgs()
        if cls.asset_id is None:
            cls.log("===== Run ====================")
            cls.asset_id = cls.callTest()
            cls.log("Asset id:", cls.asset_id)
        cls.log("===== Test ===================")


class NFTTest(NFTTestBase):
    def test_tokenMinted(self):
        asset_info = {}
        try:
            asset_info = self.algod_client.asset_info(self.asset_id)
        except:
            self.assertTrue(False, "Token not found by id")
        self.assertEqual(asset_info["params"]["creator"], self.creator_address,
                         "Creator address does not match their output")
        self.assertEqual(asset_info["params"]["decimals"], 0, "Decimals field is not 0 (is fractional)")
        self.assertTrue(asset_info["params"]["name"] == desired_asset_name or asset_info["params"]["name"] == (
                    desired_asset_name + "@arc3"), "Asset name is not as requested")
        self.assertEqual(asset_info["params"]["unit-name"], desired_unit_name, "Asset unit name is not as requested")
        self.assertEqual(asset_info["params"]["total"], 1, "Token supply is more than 1")

    def test_tokenTransfered(self):
        asset_acc_info = {}
        try:
            asset_acc_info = self.algod_client.account_asset_info(self.receiver_address, self.asset_id)
        except:
            assert False, "Token not found"
        self.assertEqual(1, asset_acc_info['asset-holding']['amount'],
                         "Receiver account does not hold asset")

if __name__ == "__main__":
    unittest.main()
