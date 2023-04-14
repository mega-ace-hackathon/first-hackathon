# PyTEALImprover: Improve PyTEAL contracts, automatically

## Problem Statement

Modify PyTEAL in order to perform whole-program optimizations. The tool will be
invoked as if it were a the upstream PyTEAL distribution.

The _improved_ program should retain _almost_ the same semantics as the original
one for an execution context with infinite gas. If the original program was
unable to handle inputs of a certain size (due to gas constraints) it is legal
to allow the _improved_ program to handle those. Allowed behavioural deviations
are documented later on this document.

The script `tests.py` will run the provided tests and show a comparison between
a regular pyteal installation and your fork.

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

## Allowed assumptions

PyTEAL has weird execution semantics. We will test only a small sample of
possible programs. In order to allow better optimization you may assume the
following things about your input contracts:

* No branching condition has side-effects (If/For/Cond)
* AST node evaluation is idempotent
* Underflow rejections dont happen
* Divide-by-zero rejections dont happen

Nonetheless, if an arithmetic manipulation causes new underflow or
divide-by-zero rejections it will be considered invalid.

## Tips

* Start with simple optimizations before doing any kind of whole program
  analysis
* Hackaton code doesn't have to be elegant, feel free to edit core AST nodes in
  ways that will never reach upstream
* Inlining and constant propagation are great enablers of other optimizations
