OUT_FILE_APPROVAL_PROGRAM = "./contracts/approval_program.teal"
OUT_FILE_CLEAR_STATE_PROGRAM = "./contracts/clear_state_program.teal"


# This example is provided for informational purposes only and has not been audited for security.

from pyteal import *


def approval_program():
    status = ScratchVar(TealType.bytes, 0)
    board1 = ScratchVar(TealType.uint64, 1)
    board2 = ScratchVar(TealType.uint64, 2)
    board3 = ScratchVar(TealType.uint64, 3)
    board4 = ScratchVar(TealType.uint64, 4)
    board5 = ScratchVar(TealType.uint64, 5)
    board6 = ScratchVar(TealType.uint64, 6)
    board7 = ScratchVar(TealType.uint64, 7)
    board8 = ScratchVar(TealType.uint64, 8)
    board9 = ScratchVar(TealType.uint64, 9)
    index = ScratchVar(TealType.uint64, 10)
    indexContract = ScratchVar(TealType.uint64, 11)

    moveContract = Cond(
        [indexContract.load() == Int(1), board1.store(Int(2))],
        [indexContract.load() == Int(2), board2.store(Int(2))],
        [indexContract.load() == Int(3), board3.store(Int(2))],
        [indexContract.load() == Int(4), board4.store(Int(2))],
        [indexContract.load() == Int(5), board5.store(Int(2))],
        [indexContract.load() == Int(6), board6.store(Int(2))],
        [indexContract.load() == Int(7), board7.store(Int(2))],
        [indexContract.load() == Int(8), board8.store(Int(2))],
        [indexContract.load() == Int(9), board9.store(Int(2))],
    )

    checkContractMove = Cond(
        [
            indexContract.load() == Int(1),
            If(board1.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(2),
            If(board2.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(3),
            If(board3.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(4),
            If(board4.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(5),
            If(board5.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(6),
            If(board6.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(7),
            If(board7.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(8),
            If(board8.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            indexContract.load() == Int(9),
            If(board9.load() != Int(0), status.store(Bytes("bad move"))),
        ],
    )

    moveUser = Cond(
        [index.load() == Int(1), board1.store(Int(1))],
        [index.load() == Int(2), board2.store(Int(1))],
        [index.load() == Int(3), board3.store(Int(1))],
        [index.load() == Int(4), board4.store(Int(1))],
        [index.load() == Int(5), board5.store(Int(1))],
        [index.load() == Int(6), board6.store(Int(1))],
        [index.load() == Int(7), board7.store(Int(1))],
        [index.load() == Int(8), board8.store(Int(1))],
        [index.load() == Int(9), board9.store(Int(1))],
    )

    checkUserMove = Cond(
        [
            index.load() == Int(1),
            If(board1.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(2),
            If(board2.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(3),
            If(board3.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(4),
            If(board4.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(5),
            If(board5.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(6),
            If(board6.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(7),
            If(board7.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(8),
            If(board8.load() != Int(0), status.store(Bytes("bad move"))),
        ],
        [
            index.load() == Int(9),
            If(board9.load() != Int(0), status.store(Bytes("bad move"))),
        ],
    )

    checkWinHR = Seq(
        If(
            And(
                board1.load() != Int(0), board1.load() == board2.load(), board2.load() == board3.load(),
            ),
            If(
                board1.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )
        ),
        If(
            And(
                board4.load() != Int(0),
                board4.load() == board5.load(), board5.load() == board6.load()
            ),
            If(
                board4.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )
        ),
        If(
            And(
                board7.load() != Int(0),
                board7.load() == board8.load(), board8.load() == board9.load()
            ),
            If(
                board7.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )
        ),
    )

    checkWinVR = Seq(
        If(
            And(board1.load() != Int(0),And(board1.load() == board4.load(), board4.load() == board7.load())),
            If(
                board1.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )
        ),
        If(
           And(board2.load() != Int(0), And(board2.load() == board5.load(), board5.load() == board8.load())),
            If(
                board2.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )
        ),
        If(
           And(board3.load() != Int(0), And(board3.load() == board6.load(), board6.load() == board9.load())),
            If(
                board3.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )
        )
    )

    checkWinDiag = Seq(
        If(
           And(board1.load() != Int(0), board1.load() == board5.load(), board5.load() == board9.load()),
            If(
                board1.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            )),
        If(
         And(board3.load() != Int(0), board3.load() == board5.load(), board5.load() == board7.load()),
            If(
                board3.load() == Int(1),
                status.store(Bytes("player won")),
                status.store(Bytes("contract won")),
            ))
    )

    return_on_cond = Seq(
        If(status.load() == Bytes("player won"), Return(Int(1))),
        If(status.load() == Bytes("contract won"), Return(Int(1))),
        If(status.load() == Bytes("bad move"), Return(Int(1))),
        If(status.load() == Bytes("draw"), Return(Int(1))),
        # If(status.load() == Bytes("playing"), Approve()),
    )

    i = ScratchVar()

    while_seq = Seq(
        index.store(GetByte(Txn.application_args[0], i.load())),
        checkUserMove,
        moveUser,
        indexContract.store(Mod(index.load() + Int(1), Int(9))),
        checkContractMove,
        moveContract,
        checkWinHR,
        checkWinVR,
        checkWinDiag,
    )

    on_creation2 = Seq(
        [
            Assert(Txn.application_args.length() == Int(1)),
            board1.store(Int(0)),
            board2.store(Int(0)),
            board3.store(Int(0)),
            board4.store(Int(0)),
            board5.store(Int(0)),
            board6.store(Int(0)),
            board7.store(Int(0)),
            board8.store(Int(0)),
            board9.store(Int(0)),
            status.store(Bytes("playing")),
            i.store(Int(0)),
            index.store(Int(0)),
            indexContract.store(Int(0)),
            While(And(i.load() < Int(9), status.load() == Bytes("playing"))).Do(
                while_seq, i.store(i.load() + Int(1))
            ),
            return_on_cond,
            status.store(Bytes("draw")),
            # index.store(GetByte(Txn.application_args[0], Int(0))),
            # setBoardUser,
            # index.store(GetByte(Txn.application_args[0], Int(1))),
            # setBoardUser,
            # board8.store(Int(1)),
            # state.store("hola"),
            Return(Int(1)),
        ]
    )

    on_creation = Seq(
        [
            App.globalPut(Bytes("Creator"), Txn.sender()),
            Assert(Txn.application_args.length() == Int(4)),
            App.globalPut(Bytes("RegBegin"), Btoi(Txn.application_args[0])),
            App.globalPut(Bytes("RegEnd"), Btoi(Txn.application_args[1])),
            App.globalPut(Bytes("VoteBegin"), Btoi(Txn.application_args[2])),
            App.globalPut(Bytes("VoteEnd"), Btoi(Txn.application_args[3])),
            Return(Int(1)),
        ]
    )

    is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes("voted"))

    on_closeout = Seq(
        [
            get_vote_of_sender,
            If(
                And(
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                    get_vote_of_sender.hasValue(),
                ),
                App.globalPut(
                    get_vote_of_sender.value(),
                    App.globalGet(get_vote_of_sender.value()) - Int(1),
                ),
            ),
            Return(Int(1)),
        ]
    )

    on_register = Return(
        And(
            Global.round() >= App.globalGet(Bytes("RegBegin")),
            Global.round() <= App.globalGet(Bytes("RegEnd")),
        )
    )

    choice = Txn.application_args[1]
    choice_tally = App.globalGet(choice)
    on_vote = Seq(
        [
            Assert(
                And(
                    Global.round() >= App.globalGet(Bytes("VoteBegin")),
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                )
            ),
            get_vote_of_sender,
            If(get_vote_of_sender.hasValue(), Return(Int(0))),
            App.globalPut(choice, choice_tally + Int(1)),
            App.localPut(Int(0), Bytes("voted"), choice),
            Return(Int(1)),
        ]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation2],
        [Txn.application_id() != Int(0), on_creation2],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(is_creator)],
        [Txn.on_completion() == OnComplete.CloseOut, on_closeout],
        [Txn.on_completion() == OnComplete.OptIn, on_register],
        [Txn.application_args[0] == Bytes("vote"), on_vote],
    )

    return program


def clear_state_program():
    get_vote_of_sender = App.localGetEx(Int(0), App.id(), Bytes("voted"))
    program = Seq(
        [
            get_vote_of_sender,
            If(
                And(
                    Global.round() <= App.globalGet(Bytes("VoteEnd")),
                    get_vote_of_sender.hasValue(),
                ),
                App.globalPut(
                    get_vote_of_sender.value(),
                    App.globalGet(get_vote_of_sender.value()) - Int(1),
                ),
            ),
            Return(Int(1)),
        ]
    )

    return program


if __name__ == "__main__":
    with open(OUT_FILE_APPROVAL_PROGRAM, "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=7)
        f.write(compiled)

    with open(OUT_FILE_CLEAR_STATE_PROGRAM, "w") as f:
        compiled = compileTeal(clear_state_program(), mode=Mode.Application, version=7)
        f.write(compiled)
