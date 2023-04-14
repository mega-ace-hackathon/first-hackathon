import os
import unittest
from unittest import TextTestRunner, TestLoader

from algosdk.v2client.algod import AlgodClient

from DevHelper import GenerateTEAL
from graviton import *
from graviton.blackbox import DryRunExecutor, ExecutionMode, DryRunInspector, DryRunTransactionParams
import hashlib
import json


DEVNET_TOKEN = "a" * 64
ALGOD_PORT = 4001

ALGOD_HOST = os.environ.get('ALGOD_HOST', 'localhost')


def get_algod() -> AlgodClient:
    return AlgodClient(DEVNET_TOKEN, f"http://{ALGOD_HOST}:{ALGOD_PORT}")


class BaseTest(unittest.TestCase):
    DRE = None
    # interface selector for the interfaceSelector interface (tonguetwister :P)
    InterfaceSelector_Selector = bytes.fromhex("4e22a3ba")

    @property
    def shortfname(self):
        return 'Test1.json'.rsplit('.', 1)[0]

    def setUp(self):
        if self.DRE is None:
            self.DRE = DryRunExecutor(get_algod(), ExecutionMode.Application, self.TEALTemplate)


class TestValidTeal(BaseTest):
    def test_validTeal(self):
        # program should be valid first of all. Attempt a dry run with default txn parameters and no input. If code has syntax errors, run will throw exception
        try:
            self.DRE.run_one([])
        except:
            self.assertTrue(False, "The code has syntax errors!")


class TestInterfaceSelector(BaseTest):
    def test_SupportsItself(self):
        inspector = self.DRE.run_one([self.InterfaceSelector_Selector, self.InterfaceSelector_Selector])
        self.assertEqual(inspector.status(), "PASS", 
                         "supportsInterface(0x4e22a3ba) should pass, as it indicates that the interface for querying interface support is implemented")

    def test_InvalidRouting_Forbidden_value(self):
        # test 0xffffffff as interface selector
        inspector = self.DRE.run_one([self.InterfaceSelector_Selector, bytes.fromhex("ffffffff")])
        self.assertEqual("REJECT", inspector.status(),
                         "0xffffffff is a forbidden value for interface selector, should reject")

    def test_InvalidRouting_Unimplemented(self):
        # test any invalid selector on supportsInterface()
        inspector = self.DRE.run_one([self.InterfaceSelector_Selector, bytes.fromhex("aaaaaaaa")])
        self.assertEqual("REJECT", inspector.status(), "any unimplemented interface selector should reject")


if __name__ == "__main__":
    runner = TextTestRunner()
    suite = unittest.TestSuite()

    def Mix(klass, teal):
        class NewTest(klass):
            TEALTemplate = teal

        NewTest.__name__ = klass.__name__
        return NewTest


    teal = GenerateTEAL('Test1.json')
    suite.addTest(TestLoader().loadTestsFromTestCase(
        Mix(TestValidTeal, teal)
    ))
    suite.addTest(TestLoader().loadTestsFromTestCase(
        Mix(TestInterfaceSelector, teal)
    ))

    results = runner.run(suite)