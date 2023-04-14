from pyteal.ast import *

_9 = Int(9)
_4 = Int(4)
_33 = Int(33)

arg_0 = Btoi(Txn.application_args[0])
program = If(arg_0, _33, _9) + _4 * If(arg_0, _9, _33)