#!/usr/bin/python3.6
import argparse
from typing import *

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


def check_solution(parseInfo: ParseInfo, solution: Solution, rankDiff: Optional[int] = None) -> bool:
    # 1) All players that are available for a day, should have an assignment
    for player in parseInfo:
        _, daysOk = parseInfo[player]
        if not any(daysOk):
            continue
        if player not in solution:
            return False

    # 2) Each player should be available during their assigned day
    for player in solution:
        _, daysOk = parseInfo[player]
        day, _ = solution[player]
        if not daysOk[day]:
            return False

    # 3) Each table should have 4 to 6 players
    tableSize: Dict[Table, int] = {}
    for player in solution:
        table, _ = solution[player]
        if table not in tableSize:
            tableSize[table] = 0
        tableSize[table] += 1
    for table in tableSize:
        if not (4 <= tableSize[table] <= 6):
            return False

    # 4) Check that the rank difference of a table does not exceed RankDiff
    if rankDiff:
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
                return False

    return True


parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

with open(args.file, 'r') as f:
    parseInfo = parse_file(f)

print(parseInfo)

