from pyteal.ast import *

x = Txn.application_args[0]
a = ScratchVar()

program = Seq(
    a.store(Seq(
        a.store(Int(0)),
        a.store(Int(1)),
        Int(3),
    )),
    a.store(Seq(
        a.store(Int(9)),
        a.load(),
    )),
    a.store(Seq(
        a.store(Btoi(x)),
        a.load(),
    )),
    Return(a.load() + Int(2)),
)