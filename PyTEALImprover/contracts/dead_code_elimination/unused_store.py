from pyteal.ast import *

x = Txn.application_args[0]
a = ScratchVar()

program = Seq(
    a.store(Int(0)),
    a.store(Int(1)),
    a.store(Int(2)),
    a.store(Int(3)),
    a.store(Int(4)),
    a.store(Int(5)),
    a.store(Btoi(x)),
    Return(a.load() + Int(2)),
)