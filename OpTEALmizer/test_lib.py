import os
import sys

from base64 import b64decode
from unittest import TestCase, TestLoader, TestResult, TestSuite, TextTestRunner, TestProgram
from subprocess import run as run_command, PIPE

from graviton.blackbox import DryRunExecutor, ExecutionMode, DryRunTransactionParams

from algosdk.v2client.algod import AlgodClient

DEVNET_TOKEN = "a" * 64
ALGOD_PORT = 4001


def get_algod() -> AlgodClient:
    ALGOD_HOST = os.environ.get('ALGOD_HOST', 'localhost')
    return AlgodClient(DEVNET_TOKEN, f"http://{ALGOD_HOST}:{ALGOD_PORT}")


algod = get_algod()


def read_file(filename):
    with open(filename) as file:
        return file.read()


def side_effects_and_results(execution, should_extract_status=True):
    result = {
        "logs": execution.logs(),
        "final_scratch": execution.final_scratch(),
        "stack_top": execution.stack_top(),
        "local_deltas": execution.local_deltas(),
        "global_delta": execution.global_delta(),
    }

    if should_extract_status:
        result["status"] = execution.status()

    return result


def bytecode_for(teal):
    response = algod.compile(teal)
    return b64decode(response["result"])


def _call_if_exists(parent, attr, *args, **kwargs):
    func = getattr(parent, attr, lambda *args, **kwargs: None)
    func(*args, **kwargs)


def improve_teal(filename):
    process = run_command(["python3", "src/main.py", filename], stdout=PIPE)
    return process.stdout.decode("utf-8")


class TealTest(TestCase):
    filename = None

    @classmethod
    def setUpClass(cls):
        cls.original_teal = read_file(cls.filename)
        cls.original_bytecode = bytecode_for(cls.original_teal)
        cls.original_executor = DryRunExecutor(algod, ExecutionMode.Application, cls.original_teal)

        cls.improved_teal = improve_teal(cls.filename)
        cls.improved_executor = DryRunExecutor(algod, ExecutionMode.Application, cls.improved_teal)
        cls.improved_bytecode = bytecode_for(cls.improved_teal)

        cls.test_results = []

    def setUp(self):
        self.executions = []

    def tearDown(self):
        self.test_results.append({
            "name": self.id(),
            "executions": self.executions,
            "original_bytecode": self.original_bytecode,
            "improved_bytecode": self.improved_bytecode,
        })

    def exec(self, *args, state={}, name=None):
        name = f"{name or len(self.executions)}"
        txn_params = DryRunTransactionParams.for_app(global_state=state)
        original_execution = self.original_executor.run_one(args, txn_params=txn_params)
        improved_execution = self.improved_executor.run_one(args, txn_params=txn_params)
        self.executions.append({
            "name": f"{name}",
            "original": original_execution,
            "improved": improved_execution,
        })

        should_extract_status = original_execution.cost() <= 700

        self.assertEqual(
            side_effects_and_results(original_execution, should_extract_status),
            side_effects_and_results(improved_execution, should_extract_status),
            f"Run {name} should preserve execution semantics",
        )

        return improved_execution


class HackatonTestResult(TestResult):
    separator1 = "=" * 70
    separator2 = "-" * 70

    def __init__(self, stream, descriptions, verbosity):
        super(HackatonTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.descriptions = descriptions
        self.verbosity = verbosity

        self.print_stats = 0 < verbosity
        self.print_teal = 1 < verbosity

    def afterSetUpClass(self, test):
        self._print(0, f"Contract {test.filename}")

        if self.print_stats:
            original_len = len(test.original_bytecode)
            improved_len = len(test.improved_bytecode)
            self._print(1, f"Original bytecode len: {original_len}")
            self._print(1, f"Improved bytecode len: {improved_len}")

        if self.print_teal:
            self._print(1, "Original TEAL")
            self.stream.writeln(self.separator2)
            self.stream.writeln(test.original_teal)
            self.stream.writeln(self.separator2)
            self._print(1, "Improved TEAL")
            self.stream.writeln(self.separator2)
            self.stream.writeln(test.improved_teal)
            self.stream.writeln(self.separator2)

        self.stream.flush()

    def startTest(self, test):
        super().startTest(test)

        self._print(1, f"Test {test._testMethodName}")
        self.stream.flush()

    def stopTest(self, test):
        super().stopTest(test)

        if self.print_stats:
            for execution in test.executions:
                original = execution["original"].cost()
                improved = execution["improved"].cost()
                name = execution["name"]
                self._print(2, f"Run {name}")
                self._print(3, f"Original cost: {original}\nImproved cost: {improved}")
        self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)

        self._print(2, "FAILED\n" + self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)

        self._print(2, "ERROR\n" + self._exc_info_to_string(err, test))

    def _print(self, level, text):
        ident = ''
        if 1 < level:
            ident = '   ' * (level - 1)

        lines = text.split('\n')

        self.stream.write(ident)
        if level != 0:
            self.stream.write(' - ')
        self.stream.writeln(lines[0])

        for line in lines[1:]:
            self.stream.write(ident)
            self.stream.write('   ')
            self.stream.writeln(line)


class HackatonSuite(TestSuite):
    def _handleClassSetUp(self, test, result):
        super(HackatonSuite, self)._handleClassSetUp(test, result)

        classSetupFailed = True
        try:
            classSetupFailed = test.__class__._classSetupFailed
        except TypeError:
            pass

        if not classSetupFailed:
            _call_if_exists(result, 'afterSetUpClass', test)


class HackatonLoader(TestLoader):
    suiteClass = HackatonSuite


class HackatonTestRunner(TextTestRunner):
    resultclass = HackatonTestResult
