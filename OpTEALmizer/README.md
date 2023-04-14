# OpTEALmizer: Improve teal contracts, automatically

## Problem Statement

Write a tool that performs program optimizations for a given teal program. The
tool will be invoked with a filepath as its only argument and should write the
_improved_ contract to standard output.

The _improved_ program should retain the same semantics as the original one for
an execution context with infinite gas. This means that if the original program
was unable to handle inputs of a certain size (due to gas constraints) it is
legal to allow the _improved_ program to handle those. Any other deviations
from the original behaviour may result in test failures.

Your provided program will be executed by running `python3 src/main.py path/to/file`.
If you need to setup your environment the setup script `python3 src/setup.py`
will be executed before any testing is done on the evaluation environment.

## Scoring

The scoring will take into account both program size (measured as **bytecode**
length, not program length) and gas costs for the provided tests. The final
score will be one fifth size improvements and four fifths gas improvements.

You can think of the scoring function as follows:
```python3
def score(test_results):
  gas_improvements = 0
  size_improvements = 0

  for original, improved in test_results:
    gas_improvements += gas_used_in_testsuite(original) - gas_used_in_testsuite(improved)
    size_improvements += len(original.bytecode) - len(improved.bytecode)

  return gas_improvements * 0.8 + size_improvements * 0.2

def gas_used_in_testuite(contract):
  total_gas = 0

  for transaction in contract.test_suite:
    total_gas += transaction.gas

  return total_gas
```

## Tests

* This repository contains **a subset** of the programs that will be used for
  the final evaluation
* The script `test.py` will use your provided program `src/main.py` to
  generate the improved contracts
* The original and improved contracts will be compared against eachother in
  gas-cost (for its corresponding testsuite) and program-size

## Tips

* Start with simple optimizations before doing any kind of whole program analysis
* Hackaton code doesn't have to be elegant, feel free to reuse available
  modules like `tealish` in unexpected ways
* Inlining and constant propagation are great enablers of other optimizations
