# Developer’s Helper: automatic TEAL templating

## Problem Statement

When starting a TEAL smart contract, there is always some code for app call routing and security checks. Its importance must not be underestimated, as many critical vulnerabilities stem from subtle mistakes in this core feature of TEAL contracts.
You are tasked with writing a python script that, given an ABI-like json file, outputs a deployable TEAL template that implements a routing mechanism for the described interfaces, that is, a series of checks and branches to the desired methods when the correct conditions are met (including number of arguments, method selector matching and call configurations as specified below).

You must make it ARC-73 compliant (https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0073.md), that is, it should implement the interface
for interface detection, as described in the ARC document.

Templated methods other than interface detection should have the following structure:
```
methodName:
X
return
```

Where the X should be filled with instructions to push the correct method selector into the top of the stack and convert it to an integer, before the program terminates succesfuly.

Valid fields for interfaces and methods are those described in ARC-4 (https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0004.md), as well as how
method and interface selectors should be computed.
For the purpose of this excercise, bare calls (calls to the contract with no arguments) are not allowed and should always fail. Also, return value implementation as described in ARC-4 is not required, input types will be ignored, and you may assume no two methods will have the same name so as to avoid any issues arising from conflicting labels.

In order to make the routing more useful, a field called _call_config_ is introduced. This field is an array of all valid call configurations for a given method.
If the array is empty, all call configurations where the method is correctly invoked should run it and pass.
If the array is non-empty, only the configurations described should pass, and any others should fail. Notice that any fields not specified in a call config are irrelevant, and therefore all possible values should be valid.
The options for a valid call config are as follows:
```
"ApplicationID": 0 [eq | neq]
"OnCompletion": [NoOp | UpdateApplication | DeleteApplication | CloseOut] [eq | neq]
"Sender": address_value [eq | neq]
"RekeyTo": address_value [eq | neq]
```
Where _eq_ represents "equal" and excludes all other options, and _neq_ represents "not equal" and excludes the specified option for the field (so all other alternatives are valid). Note that a _ClearState_ on completion action is always invalid (as described in the ARC-4 document).

Your submission must include a python script called **DevHelper.py**. It must implement a function called **GenerateTEAL(filename : str)**, which given a json file path returns a string with the generated TEAL smart contract's template.


## Tests
Testing (both secret tests and those provided to you in _DevHelperTests.py_) will be carried out using the graviton blackbox testing toolkit. To run the provided test script, you'll need to install it. Instructions are available on their official repository (https://github.com/algorand/graviton).
An example of a json file with two interface descriptions is provided (note that the interface selector interface will always be included)