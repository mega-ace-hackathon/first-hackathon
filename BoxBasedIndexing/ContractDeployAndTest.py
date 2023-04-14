import unittest

from algosdk import transaction
from algosdk.v2client import *
from pyteal import *
from beaker import *
from algosdk.transaction import *
from base64 import b64decode
from algosdk.logic import *
import random

APPROVAL_SRC = os.path.join('BoxBasedIndexing', 'contracts', "BoxBasedDB_ApprovalProgram.teal")
CLEARSTATE_SRC = os.path.join('BoxBasedIndexing', 'contracts', "BoxBasedDB_ClearStateProgram.teal")


X_ev=[4534,460,714,5587,1275,3440,1690,3517,8634,4109]

Y_ev=[2574,9931,4646,3162,243,6631,3156,7162,1937,1427]


def compileTEAL(client, code):
    compile_response = client.compile(code)
    return b64decode(compile_response['result'])


def fundApp(client, sender: sandbox.SandboxAccount, AppAddr: str, Ammount):
    txn = transaction.PaymentTxn(sender.address, sp=client.suggested_params(), receiver=AppAddr, amt=Ammount)
    signedTxn = txn.sign(sender.private_key)
    txid = client.send_transaction(signedTxn)
    wait_for_confirmation(client, signedTxn.get_txid())


def DeployAndFundApp():
    client = sandbox.get_algod_client()
    accounts = sandbox.get_accounts()

    sender = accounts[0]

    with open(APPROVAL_SRC, "r", encoding="utf-8") as f:
        approval_program = f.read()
    with open(CLEARSTATE_SRC, "r", encoding="utf-8") as f:
        clear_program = f.read()

    global_schema = StateSchema(num_uints=5, num_byte_slices=0)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)

    txn = ApplicationCreateTxn(
        sender=sender.address,
        sp=client.suggested_params(),
        on_complete=OnComplete.NoOpOC.real,
        approval_program=compileTEAL(client, approval_program),
        clear_program=compileTEAL(client, clear_program),
        app_args=[],
        global_schema=global_schema,
        local_schema=local_schema)

    signedTxn = txn.sign(sender.private_key)
    txid = client.send_transaction(signedTxn)
    response = wait_for_confirmation(client, signedTxn.get_txid())
    CreatedAppID = response["application-index"]

    fundApp(client, sender, get_application_address(CreatedAppID), 100000000000)
    return CreatedAppID


def AddMonster(AppID, monsterName, attack, defense, HP, X, Y, ASAid):
    client = sandbox.get_algod_client()
    accounts = sandbox.get_accounts()
    sender = accounts[0]

    RelevantBoxes = GetBoxes()

    txn_list = []
    signedTxnList = []
    for i in range(0, 15):
        txn = ApplicationCallTxn(
            sender=sender.address,
            index=AppID,
            sp=client.suggested_params(),
            on_complete=OnComplete.NoOpOC.real,
            app_args=["NONE"],
            boxes=RelevantBoxes[8 * i:8 * i + 8]
        )
        txn_list.append(txn)

    last_txn = ApplicationCallTxn(
        sender=sender.address,
        index=AppID,
        sp=client.suggested_params(),
        on_complete=OnComplete.NoOpOC.real,
        app_args=["CREATE", monsterName, attack, defense, HP, X, Y, ASAid],
        boxes=RelevantBoxes[-8:]
    )
    txn_list.append(last_txn)

    gid = transaction.calculate_group_id(txn_list)
    for txn in txn_list:
        txn.group = gid
        signedTxnList.append(txn.sign(sender.private_key))

    client.send_transactions(signedTxnList)

    for txn in txn_list:
        wait_for_confirmation(client, txn.get_txid())


def FindMonsterByLocation(AppID, lat, long):
    client = sandbox.get_algod_client()
    accounts = sandbox.get_accounts()
    sender = accounts[0]

    RelevantBoxes = GetBoxes()

    txn_list = []
    signedTxnList = []
    for i in range(0, 15):
        txn = ApplicationCallTxn(
            sender=sender.address,
            index=AppID,
            sp=client.suggested_params(),
            on_complete=OnComplete.NoOpOC.real,
            app_args=["NONE"],
            boxes=RelevantBoxes[8 * i:8 * i + 8]
        )
        txn_list.append(txn)

    last_txn = ApplicationCallTxn(
        sender=sender.address,
        index=AppID,
        sp=client.suggested_params(),
        on_complete=OnComplete.NoOpOC.real,
        app_args=["LOOKUP_BY_LOC", lat, long, 0],
        boxes=RelevantBoxes[-8:]
    )
    txn_list.append(last_txn)

    gid = transaction.calculate_group_id(txn_list)
    for txn in txn_list:
        txn.group = gid
        signedTxnList.append(txn.sign(sender.private_key))

    client.send_transactions(signedTxnList)

    for i in range(0, len(txn_list) - 1):
        wait_for_confirmation(client, txn_list[i].get_txid())
    finalTxnResp = wait_for_confirmation(client, txn_list[-1].get_txid())
    return finalTxnResp


def GetBoxes():
    out = []
    for i in range(0, 128):
        out.append((0, i))
    return out


def AddBatchOfMonsters(X_ev, Y_ev, AppID):
    monsters = []
    n = 0
    for x, y in zip(X_ev, Y_ev):
        name = (str(n) + "monster").zfill(12)

        ev_data = {
            "name": str(name),
            "a": int(random.randint(0, 100)), "d": int(random.randint(0,100)), "hp": int(random.randint(0, 100)),
            "X": int(x), "Y": int(y), "ASAid": n}
        monsters.append(ev_data)

        try:
            AddMonster(AppID, ev_data["name"], ev_data["a"], ev_data["d"], ev_data["hp"], ev_data["X"], ev_data["Y"], ev_data["ASAid"])
        except:
            assert False, "Adding monster failed!"
        n = n + 1
    return monsters


class BoxTest(unittest.TestCase):
    AppID = None

    def check_MonstersLoadedCorrectly(self, monsterList):
        testedMonsters = []
        shuffledIndices = list(range(len(monsterList)))
        random.shuffle(shuffledIndices)
        for h, i in enumerate(shuffledIndices):
            ev = monsterList[i]
            try:
                txnResponse = FindMonsterByLocation(AppID, ev["X"], ev["Y"])
            except:
                self.assertTrue(False, "Failed to find some monster")
            testedMonsters.append(ev)

            logResult = b64decode(txnResponse["logs"][0])
            logName = str(logResult[0:12], encoding="utf-8")

            self.assertEqual(testedMonsters[h]["name"], logName)
            for name, slice_from, slice_to in [
                ('a', 12, 20),
                ('d', 20, 28),
                ('hp', 28, 36),
                ('X', 36, 44),
                ('Y', 44, 52),
                ('ASAid', 52, 60),
            ]:
                item = int.from_bytes(logResult[slice_from:slice_to])
                self.assertEqual(testedMonsters[h][name], item)


class TestPrelimWithFewMonsters(BoxTest):
    @classmethod
    def setUpClass(cls) -> None:
        print("Adding monsters...")
        cls.AllMonsters = AddBatchOfMonsters(X_ev, Y_ev, cls.AppID)

    def test_MonstersLoadedCorrectly(self):
        print("Checking if added monsters are loaded...")
        self.check_MonstersLoadedCorrectly(self.AllMonsters)



if __name__ == "__main__":
    try:
        AppID = DeployAndFundApp()
    except:
        assert False, "Failed to deploy and fund contract. Possibly has syntax bugs, or sandbox is not running properly"
    print("APP DEPLOYED AND FUNDED CORRECTLY WITH ID ", AppID)

    TestPrelimWithFewMonsters.AppID = AppID
    unittest.main()