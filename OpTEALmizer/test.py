from unittest import main
from test_lib import TealTest, HackatonTestRunner, HackatonLoader

class ParseInt(TealTest):
    filename = "contracts/example_programs/convert_bytes_to_uint64.teal"

    def test_example(self):
        results = self.exec(state={"value": "123"}, name="Basic example")
        self.assertEqual(results.stack_top(), 123)
        results = self.exec(state={"value": "99999999999"}, name="Bigger than int32")
        self.assertEqual(results.stack_top(), 99999999999)
        results = self.exec(state={"value": "0001337"}, name="Trailing zeros")
        self.assertEqual(results.stack_top(), 1337)

    def test_negative(self):
        results = self.exec(state={"value": "-321"}, name="Negative number")
        self.assertEqual(results.status(), "REJECT")

    def test_text(self):
        results = self.exec(state={"value": "Hello world!"}, name="Non-numeric string")
        self.assertEqual(results.status(), "REJECT")

class SimpleConstantProp(TealTest):
    filename = "contracts/constant_propagation/simple.teal"

    def test_the_result_is_1337(self):
        self.assertEqual(self.exec().stack_top(), 1337)

class ConstantPropOnConditionals(TealTest):
    filename = "contracts/constant_propagation/conditionals.teal"

    def test_on_zero_the_result_is_141(self):
        self.assertEqual(self.exec(0).stack_top(), 141)

    def test_on_nonzero_the_result_is_69(self):
        self.assertEqual(self.exec(1).stack_top(), 69)
        self.assertEqual(self.exec(2).stack_top(), 69)
        self.assertEqual(self.exec(1000).stack_top(), 69)

class UnreachableCode(TealTest):
    filename = "contracts/dead_code_elimination/unreachable_code.teal"

    def test_on_zero_the_result_is_1(self):
        self.assertEqual(self.exec(0).stack_top(), 1)

    def test_on_nonzero_the_result_is_2(self):
        self.assertEqual(self.exec(1).stack_top(), 2)
        self.assertEqual(self.exec(2).stack_top(), 2)
        self.assertEqual(self.exec(1337).stack_top(), 2)

class UnusedValue(TealTest):
    filename = "contracts/dead_code_elimination/unused_value.teal"

    def test_is_the_identity_function(self):
        self.assertEqual(self.exec(0).stack_top(), 0)
        self.assertEqual(self.exec(1).stack_top(), 1)
        self.assertEqual(self.exec(100).stack_top(), 100)
        self.assertEqual(self.exec(9999999999).stack_top(), 9999999999)

class UnusedStore(TealTest):
    filename = "contracts/dead_code_elimination/unused_store.teal"

    def test_final_value_is_two_X_plus_two(self):
        self.assertEqual(self.exec(0).stack_top(), 2)
        self.assertEqual(self.exec(9).stack_top(), 20)

class ReuseValues(TealTest):
    filename = "contracts/reuse_values/reuse_values.teal"

    def encode_arr(self, arr):
        length = len(arr).to_bytes(8)
        values = [v.to_bytes(8) for v in arr]
        return b''.join([length, *values])

    def exec(self, arr, i, j):
        encoded_arr = self.encode_arr(arr)
        result = super().exec(encoded_arr, i, j)
        self.assertEqual(result.stack_top(), (arr[i]+arr[j]*len(arr))*len(arr))
        return result

    def bad_exec(self, arr, i, j):
        encoded_arr = self.encode_arr(arr)
        result = super().exec(encoded_arr, i, j)
        self.assertEqual(result.status(), "REJECT")
        return result

    def test_basic_inputs(self):
        self.exec([1, 2, 3], 0, 2)
        self.exec([9, 55, 23, 72, 5345], 4, 1)
        self.exec([9, 55, 1, 72, 5341], 2, 2)

    def test_rejected_inputs(self):
        self.bad_exec([1, 2, 3], 0, 3)
        self.bad_exec([1, 2, 3], 3, 0)
        self.bad_exec([1, 2, 3], 3, 3)

class PeepholePop(TealTest):
    filename = "contracts/peepholes/pop.teal"

    def test_final_value_is_X_plus_one(self):
        self.assertEqual(self.exec(0).stack_top(), 1)
        self.assertEqual(self.exec(1).stack_top(), 2)
        self.assertEqual(self.exec(10).stack_top(), 11)
        self.assertEqual(self.exec(999).stack_top(), 1000)

class PRIVATE__PeepholePop(TealTest):
    filename = "contracts/peepholes/pop__private.teal"

    def test_final_value_is_X_plus_one(self):
        self.assertEqual(self.exec(0).stack_top(), 1)
        self.assertEqual(self.exec(1).stack_top(), 2)
        self.assertEqual(self.exec(10).stack_top(), 11)
        self.assertEqual(self.exec(999).stack_top(), 1000)

class LoopInvariant(TealTest):
    filename = "contracts/loop_invariant/loop_invariant.teal"

    # Result 16
    def loop_invariant(self):
        # x
        self.assertEqual(self.exec(0).stack_top(), 2)
        # n
        self.assertEqual(self.exec(1).stack_top(), 4)
        # res
        self.assertEqual(self.exec(2).stack_top(), 16)

if __name__ == "__main__":
    main(testRunner=HackatonTestRunner, testLoader=HackatonLoader())