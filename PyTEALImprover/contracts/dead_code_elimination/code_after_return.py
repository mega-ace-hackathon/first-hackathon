from pyteal.ast import *

x = Txn.application_args[0]
a = ScratchVar()

program = Seq(
    Return(Int(3)),
    a.store(Int(2) + Int(9)),
    a.store(a.load() + Int(1)),
    a.store(a.load() + Int(1)),
    a.store(a.load() + Int(1)),
    a.store(a.load() + Int(1)),
    a.store(a.load() * Btoi(x)),
    Int(1),
)
