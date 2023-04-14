#!/usr/bin/env python3
"""
    Testing for Tic Tac Toe
    =======================
    We let the contract run a game on different player inputs.
    On each input we check:
    - winner is winner
    - no moves on occupied places
"""
#from algosdk import transaction, abi, account
#from algosdk.abi.address_type import AddressType
#from base64 import b64decode
from graviton import *
from graviton.blackbox import DryRunExecutor, ExecutionMode, DryRunInspector, DryRunTransactionParams, CREATION_APP_CALL, EXISTING_APP_CALL
from tests.clients import get_algod
from common import algo_init, getNodeUrl
from itertools import combinations
import unittest
import logging
import os 

#import hashlib
#import json
#import re
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
THIS_DIR = os.path.dirname(__file__)
FILENAME = os.path.join(THIS_DIR, '../contracts/approval_program.teal')
STATUS_SCRATCH = ["0"]
BOARD_PLACINGS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
PLAYERS = [1, 2]
DRAW = 3

class TTTBaseTest(unittest.TestCase):
    algod_client = None

    @classmethod
    def log(cls, *args):
        print(' '.join(str(x) for x in args), file=sys.stderr)

    @classmethod
    def setUpClass(cls) -> None:
        if cls.algod_client is None:
            cls.algod_client = algo_init(getNodeUrl(4001))
        
        #cls.args = cls.creator_address, cls.creator_private_key, cls.receiver_address, cls.receiver_private_key = getArgs()
        #if cls.asset_id is None:
        #    cls.log("===== Run ====================")
        #    # cls.asset_id = cls.callPyFile()
        #    cls.log("Asset id:", cls.asset_id)
        #    raise Exception("No asset id!")
        #cls.log("===== Test ===================")


class TTTTestSequence(TTTBaseTest):
    def test(self):
        inputs = generate_all_inputs()[0:50]
        for input_int in inputs:
            with self.subTest(msg="Running on input i", i=input_int):
                game = Game(input_int)
                _ = game.decode_game_from_scratch()
                self.assertTrue(game.assert_correct_placement())
                self.assertTrue(game.assert_correct_winner())
                self.assertTrue(game.assert_no_bad_moves())

class Game:
    def __init__(self, input):
        #logger = logging.getLogger(__name__)
        self.logger = logger
        self.gameboard = Gameboard()    # this is the tic-tac-toe boar

        # decode input
        self.input = input
        self.input_as_bytes = decode_input(input)
        logger.warning("User moved {}".format(self.input_as_bytes))

        self.inspector = None
        self.moves = []                 # decoded moves
        self.result = None              # final result
        self.contract_appointed_winner = None              # winner = 1 player, 2 contract, 3 draw

    def __generateTEAL(self):
        with open(FILENAME) as f:
            teal_code = f.read()
        return teal_code

    def __get_DryRunExecutor(self):
        # get code
        teal_code = self.__generateTEAL()
        algod = get_algod()
        dre = DryRunExecutor(algod, ExecutionMode.Application, teal_code)
        return dre

    def __get_inspector(self, dre, args):
            try:
                inspector = dre.run_one(args)
            except:
                assert(False), "Failed to get inspector. The code has syntax errors!"
            return inspector

    def _get_scratch(self):
        # init graviton's dry run executor
        dre = self.__get_DryRunExecutor()
        inspector = self.__get_inspector(dre, (self.input,))
        scratch = inspector.black_box_results.scratch_evolution
        self.inspector = inspector
        return scratch
    
    def _get_status(self, _log):
        log = _decodeLog(_log)
        if log == "player wins":
            finished = True
            winner = "player"
        elif log == "contract wins":
            finished = True
            winner = "contract"
        elif log.startswith("bad move"):
            print("logging a bad move")
            finished = False
            winner = "bad move"
        else:
            finished = False
            winner = "none"
        logger.debug("Log: {} =>>{}, {}".format(log, finished, winner))
        return (finished, winner)

    def decode_game_from_scratch(self):
        scratch = self._get_scratch()
        move = 1
        for i, s in enumerate(scratch):
            if len(s) > 0:
                print(s)                
                for j in range(len(s)):
                    k, v = s[j].split("->")
                    if k in STATUS_SCRATCH:
                        finished, winner = self._get_status(v)
                        print("status {} {}".format(finished, winner))
                        if finished:
                            self.contract_appointed_winner = winner
                            return (finished, winner)
                        elif winner.startswith("bad move"):
                            self.contract_appointed_winner = winner
                    if k in BOARD_PLACINGS:
                        player = 1 if move % 2 == 1 else 2
                        try: 
                            self.gameboard.update({k: v})
                        except Exception as e:
                            logger.debug("Game finished. Exception {}".format(e))
                            self.contract_appointed_winner = "none"
                            return (True, "none")
                        self.moves += [k]
                        logger.debug("New move {}. Moves: {}".format(k, self.moves))
                        logger.debug("Move {}. Player {} moved in {}.".format(move, v, k))

                        move += 1
                        if move > 9:
                            self.contract_appointed_winner = "draw" #review
                            return (True, "draw")
                    if k == "10":
                        logger.debug("Player updated to {}".format(v))
                    if k == "11":
                        logger.debug("Move counter updated to {}".format(v))
        logger.debug("stack ended / no more moves")
        finished = True
        #winner = "draw"
        return (finished, winner)

    #############################################################
    # These are the actual tests                                #
    #############################################################    
    def assert_correct_winner(self):
        # check if any move played on occupied
        # check if winner is correct?
        contract_appointed_winner = self.contract_appointed_winner
        winner_from_board, _ = self.gameboard.have_winner_or_draw()
        return contract_appointed_winner == winner_from_board

    def assert_no_bad_moves(self):
        # check if any move played on occupied by checking on repeated elements
        return len(set(self.moves)) == len(self.moves)

    def assert_correct_placement(self):
        # check if any move played on occupied by checking on repeated elements
        for i, m in enumerate(self.moves):
            whoplays = i % 2
            if self.gameboard.place(m) != str(whoplays + 1):
                logger.debug("Inconsistent move")
                return False
        return True
    #############################################################
    # Tests finished                                            #
    #############################################################    
    def __repr__(self):
        out = self.gameboard.__repr__()
        out += "\ncontract says:{}-script says:{}".format(self.contract_appointed_winner, self.gameboard.have_winner_or_draw()[0])
        out += "\n{}".format(self.moves)
        return out

class Gameboard(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)
    def __setitem__(self, key, val):
        print("setting {} {}".format(key, val))
        if int(key) not in range(1, 10):
            raise Exception("Gameboard:  moving in {} not allowed!".format(key))
        if int(val) not in PLAYERS:
            raise Exception("Gameboard: player {} not allowed!".format(val))
        if self.__contains__(key):
            raise Exception("Gameboard: {} occupied".format(key))
        logger.debug('Gameboard: player {} played {}'.format(key, val))
        super(Gameboard, self).__setitem__(key, val)
    def place(self, k):
        if not self.__contains__(str(k)):
            return " "
        return dict.__getitem__(self, str(k))
    def have_winner_or_draw(self):
        winner_int, finished = self.have_winner()
        if finished:
            if winner_int == "1":
                winner = "player"
            elif winner_int == "2":
                winner = "contract"
            else:
                winner = "bad move"
        elif self.board_complete():
            winner = "draw"
            finished = True
        else:
            winner, finished = ("none", False)
        return winner, finished

    def have_winner(self):
        # returns (player_int int, have_winner Boolean) 
        for x in range(3):
            first_move = self.place((x * 3) + 1)
            if (
                (self.place((x * 3) + 2) == first_move) &
                (self.place((x * 3) + 3) == first_move)
            ):
                logger.debug("Win horizontal")
                return (first_move, True)
        # check if player completed column
        # get column
        for y in range(1, 4):
            first_move = self.place(y)
            if (
                (self.place(3 + y) == first_move) &
                (self.place(6 + y) == first_move)
            ):
                logger.debug(("Win vertical"))
                return (first_move, True)
        # first diagonal
        first_move = self.place(1)
        if (
            (self.place(5) == first_move) &
            (self.place(9) == first_move)
        ):
            logger.debug(("Win diagonal 1"))
            return (first_move, True)
            # second diagonal
        first_move = self.place(3)
        if (
            (self.place(5) == first_move) &
            (self.place(7) == first_move)
        ):
            logger.debug(("Win diagonal 2"))
            return (first_move, True)
        return (0, False)

    def board_complete(self):
        if (len(self) == 9):
            return True
        else: 
            return False

    def __repr__(self):
        a = "     |     |     \n"
        a += "  {}  |  {}  |  {}  \n".format(self.place(1), self.place(2), self.place(3))
        a += "_____|_____|_____\n"
        a += "     |     |     \n"
        a += "  {}  |  {}  |  {}  \n".format(self.place(4), self.place(5), self.place(6))
        a += "_____|_____|_____\n"
        a += "     |     |     \n"
        a += "  {}  |  {}  |  {}  \n".format(self.place(7), self.place(8), self.place(9))
        a += "     |     |     "
        return a

    def __str__(self):
        return ' ,'.join((self.place(1), self.place(2), self.place(3),
                          self.place(4), self.place(5), self.place(6),
                          self.place(7), self.place(8), self.place(9))
                         )



def list_to_int(l):
    if len(l)>8:
        raise Exception("List not allowed")
    s = 0 
    for i, v in enumerate(l):
        if (v < 0) or (v > 16):
            raise Exception("Value not allowed")
        s += v * (2**(56 - (i*8)))
    return s



def _decodeLog(logline):
    return bytes.fromhex(logline.replace('0x', '')).decode('utf-8')


def generate_all_inputs():
    all_inputs = []
    # at most 5 moves for 1st player
    for game_input in combinations(BOARD_PLACINGS, 5):
        all_inputs.append(encode_input(game_input))
    return all_inputs


def encode_input(game_input):
    input_int = 0
    for n, game_move in enumerate(game_input):
        input_int += int(game_move) * int(2**(56 - (8 * n)))
    return input_int


def decode_input(input):
    return input.to_bytes((input.bit_length() + 7) // 8, 'big') or b'\0'


if __name__=="__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    unittest.main()
