# Tic-tac-toe smart contract champion

## Problem Statement
Write a smart contract for a tic-tac-toe game that does not lose. Name the contract `approval_program.teal` (mind the casing). Calls to the smart contract
must receive an `int` as input. The int is parsed by the smart contract into moves and `byte[0]` represents the first move, `byte[1]` the second move, etc.

The contract plays all the game after that single call. After registering the first move from the player, the contract must move, and then take the second
move from the player, and so on and so forth. 

The tic-tac-toe board has 9 positions. Each position in the board is encoded in  the scratch space in spaces 1,..., 9. Each scratch space entry is initialized 
with 0, which represents the empty place. When the player selects a position, this must be registered writing a 1 in the respective scratch space, and when
the contract plays this is represented by a 2.

Additionally, the smart contract must use position 0 in the scratch space to register the status of the game which may be:
- "playing": as soon as the smart contract starts to run and while it has not reached any other state.
- "player won", "contract won" or "draw": if the game has finished and the player has won, or the contract won, or the game is a draw.
- "bad move": if any of contract or player attempts to place their move on an already occupied position.

After the smart contract writes "player won", "contract won", "draw", or "bad move" to sctatch space postion 0 it should return.


## Tests
A set of tests has been encoded in `test/test.py`. Use this as a basis for your solution. More tests (now private) will be added and run to score your solution.

Tests use [graviton](https://github.com/algorand/graviton/tree/main/graviton) that must be installed for running the tests.
