from typing import Literal
import pyteal as pt


OUT_FILE_CLEAR_STATE_PROGRAM = (
    "./BoxBasedIndexing/contracts/BoxBasedDB_ClearStateProgram.teal"
)
OUT_FILE_APPROVAL_PROGRAM = (
    "./BoxBasedIndexing/contracts/BoxBasedDB_ApprovalProgram.teal"
)


# Our Monster structure
# * **Name**: 12 byte _string_
# * **Attack**: _uint64_, an integer that defines the monster’s power
# * **Defense**: _uint64_, an integer that defines the monster’s ability to defend player’s attacks
# * **HP**: _uint64_, an integer that represents the current monster’s health points
# * **Location**: _(uint64, uint64)_, a tuple of unsigned 64 bit integers that define the location of a monster in the map (Loc.X <= 10k and Loc.Y <= 10k)
# * **ASA id**: _uint64_, a unique ID that identifies the monster, and coincides with an ASA token that is given to the player dealing the final blow as a trophy.
class MonsterRecord(pt.abi.NamedTuple):
    Name: pt.abi.Field[pt.abi.String]
    Attack: pt.abi.Field[pt.abi.Uint64]
    Defence: pt.abi.Field[pt.abi.Uint64]
    Hp: pt.abi.Field[pt.abi.Uint64]
    Location: pt.abi.Field[pt.abi.StaticArray[pt.abi.Uint64, Literal[2]]]
    Asa_id: pt.abi.Field[pt.abi.Uint64]


def approval_program_():
    # Constants
    MAX_MONSTERS = 1000
    MAX_RADIUS = 250000

    # Global
    monsters_index_key = pt.Bytes("MonstersIndex")
    on_creation = pt.Seq(
        [
            pt.App.globalPut(monsters_index_key, pt.Int(0)),
            pt.Return(pt.Int(1)),
        ]
    )

    is_creator = pt.Int(1)
    on_closeout = pt.Seq([pt.Return(pt.Int(1))])

    route_none = pt.Approve()

    ## AddMonster

    @pt.Subroutine(pt.TealType.none)
    def check_unique_asaid(asa_id_to_check):
        ASAid_tp = pt.abi.make(pt.abi.Uint64)
        return pt.Seq(
            pt.For(
                i.store(pt.Int(0)),
                i.load() < pt.App.globalGet(monsters_index_key),
                i.store(i.load() + pt.Int(1)),
            ).Do(
                pt.Seq(
                    b_mr := pt.App.box_get(pt.Itob(i.load())),
                    pt.Assert(b_mr.hasValue()),
                    mr.decode(b_mr.value()),
                    mr.Asa_id.store_into(ASAid_tp),
                    pt.Assert(ASAid_tp.get() != asa_id_to_check),
                )
            ),
        )

    name = pt.abi.make(pt.abi.String)
    attack = pt.abi.make(pt.abi.Uint64)
    defense = pt.abi.make(pt.abi.Uint64)
    HP = pt.abi.make(pt.abi.Uint64)
    X = pt.abi.make(pt.abi.Uint64)
    Y = pt.abi.make(pt.abi.Uint64)
    location = pt.abi.make(pt.abi.StaticArray[pt.abi.Uint64, Literal[2]])
    ASAid = pt.abi.make(pt.abi.Uint64)
    index = pt.ScratchVar(pt.TealType.uint64)

    route_create = pt.Seq(
        pt.Assert(pt.Txn.application_args.length() == pt.Int(8)),
        index.store(pt.App.globalGet(monsters_index_key)),
        pt.Assert(index.load() < pt.Int(MAX_MONSTERS)),
        name.set(pt.Txn.application_args[1]),
        attack.decode(pt.Txn.application_args[2]),
        defense.decode(pt.Txn.application_args[3]),
        HP.decode(pt.Txn.application_args[4]),
        X.decode(pt.Txn.application_args[5]),
        pt.Assert(X.get() <= pt.Int(10000)),
        Y.decode(pt.Txn.application_args[6]),
        pt.Assert(Y.get() <= pt.Int(10000)),
        ASAid.decode(pt.Txn.application_args[7]),
        check_unique_asaid(ASAid.get()),
        location.set([X, Y]),
        (mr := MonsterRecord()).set(name, attack, defense, HP, location, ASAid),
        pt.App.box_put(pt.Itob(index.load()), mr.encode()),
        index.store(index.load() + pt.Int(1)),
        pt.App.globalPut(monsters_index_key, index.load()),
        pt.Approve(),
    )

    #     FindMonstersInLocation(“LOOKUP_BY_LOC”, uint64 X, uint64 Y, uint64 radius_squared)
    # // finds all monsters inside a given radius from the (X, Y) location and then approves the transaction.
    # // The found values should be returned through logs
    # // one result per log instruction call, as plain bytes, in the order they are passed in the AddMonster function: name | attack | defense | HP | X | Y | ASAid

    radius_squared = pt.abi.make(pt.abi.Uint64)
    X0 = pt.abi.make(pt.abi.Uint64)
    Y0 = pt.abi.make(pt.abi.Uint64)
    i = pt.ScratchVar(pt.TealType.uint64)
    attack_ = pt.ScratchVar(pt.TealType.uint64)
    mr = MonsterRecord()

    @pt.Subroutine(pt.TealType.uint64)
    def square(X, X0):
        return pt.Seq(
            pt.If(
                X > X0,
                pt.Exp(pt.Minus(X, X0), pt.Int(2)),
                pt.Exp(pt.Minus(X0, X), pt.Int(2)),
            )
        )

    find_monster = pt.Seq(
        pt.Assert(pt.Txn.application_args.length() == pt.Int(4)),
        X0.set(pt.Btoi(pt.Txn.application_args[1])),
        Y0.set(pt.Btoi(pt.Txn.application_args[2])),
        radius_squared.set(pt.Btoi(pt.Txn.application_args[3])),
        pt.Assert(radius_squared.get() < pt.Int(MAX_RADIUS)),
        pt.For(
            i.store(pt.Int(0)),
            i.load() < pt.App.globalGet(monsters_index_key),
            i.store(i.load() + pt.Int(1)),
        ).Do(
            pt.Seq(
                b_mr := pt.App.box_get(pt.Itob(i.load())),
                pt.Assert(b_mr.hasValue()),
                mr.decode(b_mr.value()),
                mr.Location.store_into(location),
                location[0].store_into(X),
                location[1].store_into(Y),
                pt.If(
                    pt.Le(
                        pt.Add(square(X.get(), X0.get()), square(Y.get(), Y0.get())),
                        radius_squared.get(),
                    ),
                    pt.Seq(
                        mr.Name.store_into(name),
                        mr.Attack.store_into(attack),
                        attack_.store(attack.get()),
                        mr.Defence.store_into(defense),
                        mr.Hp.store_into(HP),
                        mr.Asa_id.store_into(ASAid),
                        pt.Log(
                            pt.Concat(
                                name.get(),
                                attack.encode(),
                                defense.encode(),
                                HP.encode(),
                                X.encode(),
                                Y.encode(),
                                ASAid.encode(),
                            )
                        ),
                    ),
                ),
            )
        ),
        pt.Approve(),
    )

    program = pt.Cond(
        [pt.Txn.application_id() == pt.Int(0), on_creation],
        [
            pt.Txn.on_completion() == pt.OnComplete.DeleteApplication,
            pt.Return(is_creator),
        ],
        [
            pt.Txn.on_completion() == pt.OnComplete.UpdateApplication,
            pt.Return(is_creator),
        ],
        [pt.Txn.on_completion() == pt.OnComplete.CloseOut, on_closeout],
        [pt.Txn.application_args[0] == pt.Bytes("NONE"), route_none],
        [pt.Txn.application_args[0] == pt.Bytes("CREATE"), route_create],
        [pt.Txn.application_args[0] == pt.Bytes("LOOKUP_BY_LOC"), find_monster],
    )

    return program


def clear_program_():
    program = pt.Approve()
    return program


def compile() -> None:
    # approval_program, clear_program, contract = router.compile_program(version=8)
    approval_program = pt.compileTeal(
        approval_program_(), mode=pt.Mode.Application, version=8
    )
    clear_program = pt.compileTeal(
        clear_program_(), mode=pt.Mode.Application, version=8
    )
    # print(app_build.approval_program)
    with open(OUT_FILE_APPROVAL_PROGRAM, "w") as f:
        f.write(approval_program)

    with open(OUT_FILE_CLEAR_STATE_PROGRAM, "w") as f:
        f.write(clear_program)


if __name__ == "__main__":
    compile()
