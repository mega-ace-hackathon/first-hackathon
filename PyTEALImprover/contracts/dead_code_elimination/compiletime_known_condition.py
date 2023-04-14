from pyteal.ast import *


always_is_one = If(Int(0), Int(9999), Int(1))
always_is_two = If(Int(1), Int(2),    Int(9999))
always_is_three = Cond(
    [Int(0) == Int(1), Int(999)],
    [Int(2) == Int(3), Int(998)],
    [Int(3) == Int(3), Int(3)],
)

program = always_is_one + always_is_two + always_is_three