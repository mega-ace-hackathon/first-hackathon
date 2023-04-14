# Augmented Reality Game with Box Based Indexing

## Problem Statement

An augmented reality (AR) game is a type of video game that blends the virtual world with the real world. It uses the gps, camera and sensors of a mobile device, such as a smartphone or a tablet, to overlay digital images or graphics onto the real-world environment (a prominent example is Pokémon Go).

You’ll be tasked with implementing an on-chain system to store and manage monster locations, and by which players can query their immediate surroundings for monsters to fight against.
The city’s gaming zone should be modeled as a square area _(0, 0)_ to _(10000m, 10000m)_, all coordinates positive integers.
The monsters themselves are modeled as structures with the following fields:
* **Name**: 12 byte _string_
* **Attack**: _uint64_, an integer that defines the monster’s power
* **Defense**: _uint64_, an integer that defines the monster’s ability to defend player’s attacks
* **HP**: _uint64_, an integer that represents the current monster’s health points
* **Location**: _(uint64, uint64)_, a tuple of unsigned 64 bit integers that define the location of a monster in the map (Loc.X <= 10k and Loc.Y <= 10k)
* **ASA id**: _uint64_, a unique ID that identifies the monster, and coincides with an ASA token that is given to the player dealing the final blow as a trophy.

The smart contract should have 3 functions (arguments in AppArgs order):

```
NoOp(“NONE”)
//always approves the transaction and does nothing else (will be used to increase transaction budget)

AddMonster(“CREATE”, string name, uint64 attack, uint64 defense, uint64 HP, uint64 X, uint64 Y, uint64 ASAid)
//adds a monster to the map and approves the transaction if succesful

FindMonstersInLocation(“LOOKUP_BY_LOC”, uint64 X, uint64 Y, uint64 radius_squared)
// finds all monsters inside a given radius from the (X, Y) location and then approves the transaction. 
// The found values should be returned through logs
// one result per log instruction call, as plain bytes, in the order they are passed in the AddMonster function: name | attack | defense | HP | X | Y | ASAid
```

Inner transactions are not allowed, so the maximum op budget the contract can use is 11200 (an atomic group txn of size 16).
When boxes are used, their names should be the integers 0…127 taken as unsigned 64 bit integers (for the maximum amount of boxes available). Note that this refers to the integers themselves and not a string. For example, a box named “10” is invalid, but a box named 10 (_0x000000000000000A_ in hex) is valid.

The system should be able to accommodate up to 1000 independent monsters at once. You may assume they’ll be distributed uniformly across the available space, and the radius query has a maximum reach of _500m_ (that is, the radius_squared parameter is such that r^2 <= 250000).

Your submission must include a file named **BoxBasedDB_ApprovalProgram.teal**, where your logic is implemented.


## Tests

Testing will be carried inside a sandbox instance by deploying the app, funding it with _10e+12_ micro algos. Calls to _AddMonster(...)_ and _FindMonstersInLocation(...)_ will be made as groups of 16 txns, with 15 _NoOp_ txns preceding the relevant function call, and the 16th having the required values as application arguments (to be retrieved in contract using: _txna ApplicationArgs [X]_) in the order they appear in the function prototype. Each txn in the group will also have a boxes array, amounting to 128 references to all the allowed boxes in the problem (with the naming convention described above).
Note that the app should take no arguments on the creation txn, tho it may set up any variables you consider necessary.
A test that fails to complete because of box read / write budget or opcode limitations is considered failed (as well as any call that logs the data erroneously).

You are provided with a script to deploy and fund the app, as well as a simple test to check if a series of 10 monsters were correctly added or not.