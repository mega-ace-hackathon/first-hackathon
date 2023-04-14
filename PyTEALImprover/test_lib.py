import os
import sys

from base64 import b64decode
from multiprocessing import Pipe, Process
from runpy import run_path
from unittest import TestCase, TestLoader, TestResult, TestSuite, TextTestRunner, TestProgram

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

class PyTEALCompiler:
    def __init__(self, is_improved_pyteal):
        self.is_improved_pyteal = is_improved_pyteal
        self.parent_conn, self.loop_conn = Pipe()
        self.loop_process = Process(target=self._loop)
        self.loop_process.start()

    def _loop(self):
        if self.is_improved_pyteal:
            sys.path.insert(0, 'pyteal')

        from pyteal import OptimizeOptions, Mode, compileTeal
        while True:
            try:
                (filename, mode, version, assembleConstants, optimize) = self.loop_conn.recv()
                mode = getattr(Mode, mode)
                optimize = OptimizeOptions(**optimize) if optimize is not None else None
                ast = run_path(filename)["program"]
                teal_code = compileTeal(ast, mode, version=version, assembleConstants=assembleConstants, optimize=optimize)
                self.loop_conn.send(teal_code)
            except Exception as e:
                self.loop_conn.send(e)

    def compile_teal(self, filename, mode, *, version=2, assembleConstants=False, optimize=None):
        self.parent_conn.send((filename, mode, version, assembleConstants, optimize))
        result = self.parent_conn.recv()
        if isinstance(result, Exception):
            raise result
        return result

    def stop(self):
        self.loop_process.terminate()

def _call_if_exists(parent, attr, *args, **kwargs):
    func = getattr(parent, attr, lambda *args, **kwargs: None)
    func(*args, **kwargs)

compilers = {}

def compiler(is_improved_pyteal):
    if compilers.get(is_improved_pyteal) is None:
        compilers[is_improved_pyteal] = PyTEALCompiler(is_improved_pyteal)
    return compilers[is_improved_pyteal]

def stop_compilers():
    for compiler in compilers.values():
        compiler.stop()
    compilers.clear()

class PyTEALTest(TestCase):
    filename = None

    @classmethod
    def setUpClass(cls):
        cls.original_teal = compiler(False).compile_teal(cls.filename, "Application", version=8)
        cls.original_bytecode = bytecode_for(cls.original_teal)
        cls.original_executor = DryRunExecutor(algod, ExecutionMode.Application, cls.original_teal)

        cls.improved_teal = compiler(True).compile_teal(cls.filename, "Application", version=8)
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

    def run(self, test):
        try:
            return super().run(test)
        finally:
            stop_compilers()