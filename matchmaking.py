# Copyright 2019 Cyril Six. Subject to the GNU GPL v3 license.

import argparse
from typing import *
from timeout import timeout, TimeoutError
from itertools import permutations
from statistics import mean, stdev
import random as rd
import sys

# https://pypi.org/project/recordclass/
from recordclass import recordclass, RecordClass # type: ignore

seed = rd.randrange(sys.maxsize)
#seed = 3399729631327393780
rng = rd.Random(seed)
print("Seed:", seed)

nDays = 2 # number of available days

Name = str
Score = float
Rank = int
DaysOk = List[bool]
class PlayerInfo():
    def __init__(self, score: Score, daysOk: DaysOk) -> None:
        self.score = score
        self.daysOk = daysOk
        self._rank: Union[None, Rank] = None

    def get_rank(self) -> Rank:
        s = self.score
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

    @property
    def rank(self) -> Rank:
        if self._rank is None:
            self._rank = self.get_rank()
        return self._rank


PI = PlayerInfo
PlayersInfo = Dict[Name, PlayerInfo]

def remove_all(L: List[Any], x: Any) -> None:
    length = len(L)
    i = 0
    while i < len(L):
        if L[i] == x:
            L.remove(L[i])
            continue
        i+=1

def parse_file (f) -> PlayersInfo:
    playersInfo: PlayersInfo = {}
    for line in f:
        line = line.replace('\t', '    ')
        words = line.split(' ')
        remove_all(words, '')
        name = ''.join(words[0:-3]).replace('{', '').replace('}', '').replace('|', '')
        print(words)
        score = float(words[-3])
        daysOk = [bool(int(words[-2])), bool(int(words[-1]))]
        if not any(daysOk):
            continue

        assert(name not in playersInfo)
        playersInfo[name] = PI(score, daysOk)
    return playersInfo

Day = int
Table = int
class PlayerAssign(RecordClass):
    day: Day
    table: Table
PA = PlayerAssign
Solution = Dict[Name, PlayerAssign]


def _check_solution(playersInfo: PlayersInfo, solution: Solution, rankDiff: Optional[int] = None) -> int:
    # 1) All players that are available for a day, should have an assignment
    for playerName in playersInfo:
        if playerName not in solution:
            return -1

    # 2) Each player should be available during their assigned day
    for playerName in solution:
        player = playersInfo[playerName]
        day, _ = solution[playerName]
        if not player.daysOk[day]:
            return -2

    # 3) Each table should have 4 to 6 players
    tableSize: Dict[Table, int] = {}
    for playerName in solution:
        _, table = solution[playerName]
        if table not in tableSize:
            tableSize[table] = 0
        tableSize[table] += 1
    for table in tableSize:
        if not (4 <= tableSize[table] <= 6):
            return -3

    # 4) Check that the rank difference of a table does not exceed RankDiff
    if rankDiff is not None:
        tableRankRange: Dict[Table, Tuple[int, int]] = {}
        for playerName in solution:
            table, _ = solution[playerName]
            player = playersInfo[playerName]
            if table not in tableRankRange:
                tableRankRange[table] = (player.rank, player.rank)

            rankRange = tableRankRange[table]
            if player.rank < rankRange[0]:
                rankRange = (player.rank, rankRange[1])
            elif player.rank > rankRange[1]:
                rankRange = (rankRange[0], player.rank)
            tableRankRange[table] = rankRange

        for table in tableRankRange:
            rankRange = tableRankRange[table]
            tableDiff = rankRange[1] - rankRange[0]
            if tableDiff > rankDiff:
                return -4

    # 5) Each player should not be allocated to more than one table
    # --> already guaranteed by the dictionary structure

    return 0


def check_solution(playersInfo: PlayersInfo, solution: Solution, rankDiff: Optional[int] = None) -> bool:
    return (_check_solution(playersInfo, solution, rankDiff) == 0)


def test_check_solution() -> None:
    playersInfo = {"toto": PI(0., [False, True]), "titi": PI(0., [False, True]), "tata": PI(0., [False, True]), "lolo": PI(0., [True, True])}

    solution = {"toto": PA(1, 0), "titi": PA(1, 0), "tata": PA(1, 0), "lolo": PA(1, 0)}
    assert(_check_solution(playersInfo, solution, 0) == 0) # success

    solution = {"toto": PA(1, 0), "tata": PA(1, 0), "lolo": PA(1, 0)}
    assert(_check_solution(playersInfo, solution, 0) == -1) # fail 1)

    solution = {"toto": PA(0, 0), "titi": PA(0, 0), "tata": PA(0, 0), "lolo": PA(0, 0)}
    assert(_check_solution(playersInfo, solution, 0) == -2) # fail 2)

    playersInfo = {"toto": PI(0., [False, True]), "titi": PI(0., [False, True]), "tata": PI(0., [False, True])}
    solution = {"toto": PA(1, 0), "titi": PA(1, 0), "tata": PA(1, 0)}
    assert(_check_solution(playersInfo, solution, 0) == -3) # fail 3)

    playersInfo = {"toto": PI(10., [False, True]), "titi": PI(0., [False, True]), "tata": PI(0., [False, True]), "lolo": PI(0., [True, True])}
    solution = {"toto": PA(1, 0), "titi": PA(1, 0), "tata": PA(1, 0), "lolo": PA(1, 0)}
    assert(_check_solution(playersInfo, solution, 0) == -4) # fail 4)

    print("All good!")


def print_solution(playersInfo: PlayersInfo, solution: Solution) -> None:
    tables : Dict[int, Tuple[Day, List[Name]]] = {}
    for player in solution:
        day, table = solution[player]
        if table not in tables:
            tables[table] = (day, [])
        tables[table][1].append(player)

    for table in tables:
        print("Table", table, "of day", tables[table][0])
        for player in tables[table][1]:
            print("    ", player, "\t", playersInfo[player].score)



# Example: cut_by_four(11)
def cut_by_four(n: int) -> Optional[List[int]]:
    assert(n >= 0)
    if n in [0, 1, 2, 3, 7]:
        return None
    nPerfect = int(n/4) # 2
    L = [4] * nPerfect # [4, 4]
    L.append(n - nPerfect*4) # [4, 4, 3]
    if L[-1] < 4: # yes
        while L[-1] != 0: # yes | no
            for i in range(L[-1]): # range is [0, 1, 2] | [0]
                L[i] += 1
                L[-1] -= 1
            # after the for loop: [5, 5, 1] | [6, 5, 0]
        # after the while loop: [6, 5, 0]
        L.pop(len(L) - 1) # [6, 5]
    return L


def get_days(daysOk: List[bool]) -> List[Day]:
    return [day for day in [0, 1] if daysOk[day]]


# Sort by score, randomizing players of equal score
def partial_sort_score(playersInfo: PlayersInfo) -> List[Name]:
    playersOfScore: Dict[float, List[Name]] = {}
    for player in playersInfo:
        score = playersInfo[player].score
        if score not in playersOfScore:
            playersOfScore[score] = []
        playersOfScore[score].append(player)

    for score in playersOfScore:
        rng.shuffle(playersOfScore[score])

    players = []
    for score in sorted(playersOfScore.keys(), reverse=True):
        players.extend(playersOfScore[score])

    return players


def deduce_day(playersInfo: PlayersInfo, players: List[Name]) -> Optional[Day]:
    day = None
    for player in players:
        days = get_days(playersInfo[player].daysOk)
        if len(days) == 1:
            if day is None:
                day = days[0]
            elif day != days[0]:
                return None
    if day is None:
        day = rng.randint(0, 1)
    return day


def table_ok(playersInfo: PlayersInfo, players: List[Name]) -> bool:
    return deduce_day(playersInfo, players) != None


##
# Seek a player to swap in upId
# seek a swapping partner in downId, and swap them
# Continue the process as long as the table upId isn't ok
# Returns true if it actually managed to correctify the table
# /!\ Supposes the players in upId and downId are already sorted by score /!\
##
def seek_and_swap_players(playersInfo: PlayersInfo, upId: Table, downId: Table,
                          tables: List[List[Name]], reverse: bool = False) -> bool:
    swapPlayerFound = True
    while not (table_ok(playersInfo, tables[upId]) or (not swapPlayerFound)):
        # Seeking upIdPlayer
        upIdDay = None
        upIdPlayer = None
        upIdPi = None
        for pi, player in enumerate(tables[upId]):
            days = get_days(playersInfo[player].daysOk)
            if len(days) == 1:
                if upIdDay is None:
                    upIdDay = days[0]
                elif upIdDay != days[0]:
                    upIdPlayer = player
                    upIdPi = pi
                    upIdPlayerDay = days[0]
                    break
        assert(upIdPlayer is not None)

        # Seeking downIdPlayer
        swapPlayerFound = False
        iterPlayers = enumerate(tables[downId])
        if reverse:
            iterPlayers = reversed(list(iterPlayers))
        for pi, player in iterPlayers:
            days = get_days(playersInfo[player].daysOk)
            if len(days) == 2 or (len(days) == 1 and days[0] != upIdPlayerDay):
                # do the swap
                tables[upId][upIdPi] = player
                tables[downId][pi] = upIdPlayer
                swapPlayerFound = True
                break

    return table_ok(playersInfo, tables[upId])


##
# Perform swaps in order to correctify the solution
##
def correctify_solution(playersInfo: PlayersInfo, tables: List[List[Name]]) -> Optional[Solution]:
    for i in range(len(tables)-1):
        if not table_ok(playersInfo, tables[i]):
            seek_and_swap_players(playersInfo, i, i+1, tables)

    # Reordering before tackling reverse pass
    for table in tables:
        table.sort(key=lambda name: playersInfo[name].score, reverse=True)

    # Reverse pass
    for i in reversed(range(1, len(tables))):
        if not table_ok(playersInfo, tables[i]):
            success = seek_and_swap_players(playersInfo, i, i-1, tables, reverse=True)
            if not success:
                return None

    if not table_ok(playersInfo, tables[0]):
        return None

    solution = {}
    for i, tablePlayers in enumerate(tables):
        day = deduce_day(playersInfo, tablePlayers)
        assert(day is not None)
        for player in tablePlayers:
            solution[player] = PA(day, i)

    return solution


def group_players(playersInfo: PlayersInfo) -> Optional[List[List[Name]]]:
    tables: List[List[Name]] = []
    cutByFour = cut_by_four(len(playersInfo.keys()))
    if cutByFour is None:
        return None
    groupSizes = sorted(cutByFour, reverse=True)
    players = partial_sort_score(playersInfo)
    playerIndex = 0
    for groupSize in groupSizes:
        tables.append(players[playerIndex:playerIndex+groupSize])
        playerIndex += groupSize
    return tables


def group_and_swap_solution(playersInfo: PlayersInfo) -> Optional[Solution]:
    tables = group_players(playersInfo)
    if tables is None:
        return None
    return correctify_solution(playersInfo, tables)


def to_bool_list(n: int, size: int) -> List[bool]:
    assert (n >= 0)
    bools = []
    while (n > 0):
        bools.append(bool(n%2))
        n = int(n/2)
    while len(bools) < size:
        bools.append(False)
    bools.reverse()
    return bools


def create_tables_fixed_days(playersInfo: PlayersInfo, day1Players: List[Name],
                             day2Players: List[Name]) -> Optional[List[List[Name]]]:
    if len(day1Players) > 0:
        tablesDay1 = group_players({player: playersInfo[player] for player in day1Players})
        if tablesDay1 is None:
            return None
    else:
        tablesDay1 = []

    if len(day2Players) > 0:
        tablesDay2 = group_players({player: playersInfo[player] for player in day2Players})
        if tablesDay2 is None:
            return None
    else:
        tablesDay2 = []

    return tablesDay1 + tablesDay2


def get_tables_score(playersInfo: PlayersInfo, tables: List[List[Name]]) -> Tuple[float, float]:
    playerScores = [[playersInfo[player].score for player in table] for table in tables]
    score = 0.0
    for table in playerScores:
        score -= max(table) * sum([max(table)-pl for pl in table])

    # Subscore: comparing the stdev of the two best tables
    tablesSorted = sorted(playerScores, key=max, reverse=True)
    subscore = -stdev([mean(table) for table in tablesSorted[0:2]])
    return (score, subscore)


@timeout(30)
def exhaustive_search(playersInfo: PlayersInfo) -> Optional[Solution]:
    bestTables = None
    day1Only = [player for player in playersInfo
                       if playersInfo[player].daysOk == [True, False]]
    day2Only = [player for player in playersInfo
                       if playersInfo[player].daysOk == [False, True]]
    day12 = [player for player in playersInfo
                    if playersInfo[player].daysOk == [True, True]]
    for daysIter in range(2**len(day12)):
        if len(day12) == 0:
            day1Players = list(day1Only)
            day2Players = list(day2Only)
            bestTables = create_tables_fixed_days(playersInfo, day1Players, day2Players)
            if bestTables is None:
                continue
            bestScore = get_tables_score(playersInfo, bestTables)
            break
        dayDecisions = to_bool_list(daysIter, len(day12))
        day1Players = list(day1Only)
        day2Players = list(day2Only)
        for i, player in enumerate(day12):
            if dayDecisions[i]:
                day2Players.append(player)
            else:
                day1Players.append(player)
        tables = create_tables_fixed_days(playersInfo, day1Players, day2Players)
        if tables is None:
            continue
        score = get_tables_score(playersInfo, tables)
        if bestTables is None or score > bestScore:
            bestTables = [tables] # type: ignore
            bestScore = score
        elif score == bestScore:
            bestTables.append(tables) # type: ignore
        #if score==bestScore:
        #    print(80*"-")
        #    print(tables)
        #    print("\t", score)

    #print("best score:", bestScore)
    if bestTables is None:
        return None
    tables = rng.choice(bestTables) # type: ignore
    solution = {}
    for i, tablePlayers in enumerate(tables): # type: ignore
        day = deduce_day(playersInfo, tablePlayers)
        assert(day is not None)
        for player in tablePlayers:
            solution[player] = PA(day, i)
    return solution


def compute_solution(playersInfo: PlayersInfo) -> Optional[List[Solution]]:
    solutions = []
    try:
        solution = exhaustive_search(playersInfo)
        if solution is not None:
            print(20*"#" + " exhaustive search suggestion " + 20*"#")
            print_solution(playersInfo, solution)
            solutions.append(solution)
        else:
            print("Exhaustive search failed (No solution)")
    except TimeoutError as msg:
        print("Exhaustive search failed (timeout)")
        pass
    for i in range(100):
        solution = group_and_swap_solution(playersInfo)
        if solution is not None and check_solution(playersInfo, solution):
            print(20*"#" + " group_and_swap suggestion " + 20*"#")
            print_solution(playersInfo, solution)
            solutions.append(solution)
            break
    if solution is None:
        print("group_and_swap failed (No solution)")
    return solutions

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

if args.file == "test":
    test_check_solution()
    sys.exit(0)

with open(args.file, 'r') as f:
    playersInfo = parse_file(f)

# Some debug prints
print({player: playersInfo[player].score for player in playersInfo})
day1Only = [player for player in playersInfo if playersInfo[player].daysOk == [True, False]]
day2Only = [player for player in playersInfo if playersInfo[player].daysOk == [False, True]]
day12 = [player for player in playersInfo if playersInfo[player].daysOk == [True, True]]
print("day1 only:", day1Only)
print("day2 only:", day2Only)
print("both days:", day12)
print(80*"-")

solutions = compute_solution(playersInfo)
if solutions is None:
    print("No fitting solution could be found.")
else:
    for i, solution in enumerate(solutions):
        if not check_solution(playersInfo, solution):
            print("/!\\ The solution {} is not valid /!\\".format(str(i)))
    print(30*"-" + " SUGGESTED " + 30*"-")
    print_solution(playersInfo, solutions[0])

