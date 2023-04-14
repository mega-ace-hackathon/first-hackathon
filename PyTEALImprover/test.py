from unittest import main
from test_lib import PyTEALTest, HackatonTestRunner, HackatonLoader

class SimpleConstantProp(PyTEALTest):
    filename = "contracts/constant_propagation/simple.py"

    def test_the_result_is_1337(self):
        self.assertEqual(self.exec(name="on any input").stack_top(), 1337)

class ConstantPropOnConditionals(PyTEALTest):
    filename = "contracts/constant_propagation/conditionals.py"

    def test_on_zero_the_result_is_141(self):
        self.assertEqual(self.exec(0, name="on 0").stack_top(), 141)

    def test_on_nonzero_the_result_is_69(self):
        self.assertEqual(self.exec(1, name="on 1").stack_top(), 69)
        self.assertEqual(self.exec(2, name="on 2").stack_top(), 69)
        self.assertEqual(self.exec(1000, name="on 1000").stack_top(), 69)

class UnusedStore(PyTEALTest):
    filename = "contracts/dead_code_elimination/unused_store.py"

    def test_basic_tests(self):
        self.assertEqual(self.exec(0, name="on 0").stack_top(), 2)
        self.assertEqual(self.exec(10, name="on 10").stack_top(), 12)
        self.assertEqual(self.exec(998, name="on 998").stack_top(), 1000)

class UnusedNestedStore(PyTEALTest):
    filename = "contracts/dead_code_elimination/unused_store_nested.py"

    def test_basic_tests(self):
        self.assertEqual(self.exec(0, name="on 0").stack_top(), 2)
        self.assertEqual(self.exec(10, name="on 10").stack_top(), 12)
        self.assertEqual(self.exec(998, name="on 998").stack_top(), 1000)

class CodeAfterReturn(PyTEALTest):
    filename = "contracts/dead_code_elimination/code_after_return.py"

    def test_basic_tests(self):
        self.assertEqual(self.exec(0, name="on 0").stack_top(), 3)
        self.assertEqual(self.exec(10, name="on 10").stack_top(), 3)
        self.assertEqual(self.exec(998, name="on 998").stack_top(), 3)

class CompiletimeKnownCondition(PyTEALTest):
    filename = "contracts/dead_code_elimination/compiletime_known_condition.py"

    def test_returns_six(self):
        self.assertEqual(self.exec().stack_top(), 6)

if __name__ == "__main__":
    main(testRunner=HackatonTestRunner, testLoader=HackatonLoader())