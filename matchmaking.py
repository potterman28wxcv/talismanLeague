#!/usr/bin/python3.6
import argparse
from typing import *
import random as rd
import sys

seed = rd.randrange(sys.maxsize)
seed = 4209056135191916808
rng = rd.Random(seed)
print("Seed:", seed)

Name = str
Score = float
DaysOk = List[bool]
PlayerInfo = Tuple[Score, DaysOk]
ParseInfo = Dict[Name, PlayerInfo]

def parse_file (f) -> ParseInfo:
    parseInfo: ParseInfo = {}
    for line in f:
        words = line.split(' ')
        name = ''.join(words[0:-3]).replace('{', '').replace('}', '').replace('|', '')
        score = float(words[-3])
        daysOk = [bool(words[-2]), bool(words[-1])]
        if not any(daysOk):
            continue

        assert(name not in parseInfo)
        parseInfo[name] = (score, daysOk)
    return parseInfo

Rank = int
def score_to_rank(s: Score) -> Rank:
    assert (s >= 0.0)
    if (s < 10.0):
        return 0
    elif (s < 20.0):
        return 1
    elif (s < 35.0):
        return 2
    elif (s < 50.0):
        return 3
    else:
        return 4


Day = int
Table = int
PlayerAssign = Tuple[Day, Table]
Solution = Dict[Name, PlayerAssign]


def _check_solution(parseInfo: ParseInfo, solution: Solution, rankDiff: Optional[int] = None) -> int:
    # 1) All players that are available for a day, should have an assignment
    for player in parseInfo:
        _, daysOk = parseInfo[player]
        if player not in solution:
            return -1

    # 2) Each player should be available during their assigned day
    for player in solution:
        _, daysOk = parseInfo[player]
        day, _ = solution[player]
        if not daysOk[day]:
            return -2

    # 3) Each table should have 4 to 6 players
    tableSize: Dict[Table, int] = {}
    for player in solution:
        table, _ = solution[player]
        if table not in tableSize:
            tableSize[table] = 0
        tableSize[table] += 1
    for table in tableSize:
        if not (4 <= tableSize[table] <= 6):
            return -3

    # 4) Check that the rank difference of a table does not exceed RankDiff
    if rankDiff is not None:
        tableRankRange: Dict[Table, Tuple[int, int]] = {}
        for player in solution:
            table, _ = solution[player]
            score, _ = parseInfo[player]
            rank = score_to_rank(score)
            if table not in tableRankRange:
                tableRankRange[table] = (rank, rank)

            rankRange = tableRankRange[table]
            if rank < rankRange[0]:
                rankRange = (rank, rankRange[1])
            elif rank > rankRange[1]:
                rankRange = (rankRange[0], rank)
            tableRankRange[table] = rankRange

        for table in tableRankRange:
            rankRange = tableRankRange[table]
            tableDiff = rankRange[1] - rankRange[0]
            if tableDiff > rankDiff:
                return -4

    return 0


def check_solution(parseInfo: ParseInfo, solution: Solution, rankDiff: Optional[int] = None) -> bool:
    return (_check_solution(parseInfo, solution, rankDiff) == 0)


def test_check_solution() -> None:
    parseInfo = {"toto": (0., [False, True]), "titi": (0., [False, True]), "tata": (0., [False, True]), "lolo": (0., [True, True])}

    solution = {"toto": (1, 0), "titi": (1, 0), "tata": (1, 0), "lolo": (1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == 0) # success

    solution = {"toto": (1, 0), "tata": (1, 0), "lolo": (1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -1) # fail 1)

    solution = {"toto": (0, 0), "titi": (0, 0), "tata": (0, 0), "lolo": (0, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -2) # fail 2)

    parseInfo = {"toto": (0., [False, True]), "titi": (0., [False, True]), "tata": (0., [False, True])}
    solution = {"toto": (1, 0), "titi": (1, 0), "tata": (1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -3) # fail 3)

    parseInfo = {"toto": (10., [False, True]), "titi": (0., [False, True]), "tata": (0., [False, True]), "lolo": (0., [True, True])}
    solution = {"toto": (1, 0), "titi": (1, 0), "tata": (1, 0), "lolo": (1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -4) # fail 4)

    print("All good!")


def choose_random_solution(parseInfo: ParseInfo) -> Solution:
    solution = {}
    nDays = 0
    for player in parseInfo:
        score, daysOk = parseInfo[player]
        nDays = len(daysOk)
        break

    tableSizeDay : Dict[Day, Dict[Table, int]] = {day: {} for day in range(nDays)}
    tableCounterDay : Dict[Day, Table] = {day: 0 for day in range(nDays)}

    for player in parseInfo:
        score, daysOk = parseInfo[player]
        availableDays: List[Day] = [day for day, ok in enumerate(daysOk) if ok]
        day = rng.choice(availableDays)

        tableSize = tableSizeDay[day]
        tableCounter = tableCounterDay[day]

        if len(tableSize) == 0:
            tableSize[tableCounter] = 0
            tableCounterDay[day] += 1
        table = rng.choice(list(tableSize.keys()))
        tableSize[table] += 1
        if tableSize[table] == 6:
            tableSize.pop(table)

        table += 100*day # FIXME - terrible hack for ensuring tables of different days do not overlap..

        solution[player] = (day, table)
    return solution


parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

if args.file == "test":
    test_check_solution()
    sys.exit(0)

with open(args.file, 'r') as f:
    parseInfo = parse_file(f)

print(parseInfo)

count=0
while True: # do-while
    solution = choose_random_solution(parseInfo)
    if count <= 10000:
        if check_solution(parseInfo, solution, 0):
            break
    elif count <= 20000:
        if check_solution(parseInfo, solution, 1):
            break
    elif count <= 30000:
        if check_solution(parseInfo, solution, 2):
            break
    elif count <= 40000:
        if check_solution(parseInfo, solution, 3):
            break
    else:
        print("Could not find a solution :-(")
        break
    count += 1

print(solution)
