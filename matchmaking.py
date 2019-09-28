#!/usr/bin/python3.6
import argparse
from typing import *
from itertools import permutations
from statistics import mean
import random as rd
import sys

# https://pypi.org/project/recordclass/
from recordclass import recordclass, RecordClass # type: ignore

seed = rd.randrange(sys.maxsize)
seed = 4209056135191916808
rng = rd.Random(seed)
print("Seed:", seed)

nDays = 2 # number of available days

Name = str
Score = float
DaysOk = List[bool]
class PlayerInfo(RecordClass):
    score: Score
    daysOk: DaysOk
PI = PlayerInfo
ParseInfo = Dict[Name, PlayerInfo]

def parse_file (f) -> ParseInfo:
    parseInfo: ParseInfo = {}
    for line in f:
        words = line.split(' ')
        name = ''.join(words[0:-3]).replace('{', '').replace('}', '').replace('|', '')
        score = float(words[-3])
        daysOk = [bool(int(words[-2])), bool(int(words[-1]))]
        if not any(daysOk):
            continue

        assert(name not in parseInfo)
        parseInfo[name] = PI(score, daysOk)
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
class PlayerAssign(RecordClass):
    day: Day
    table: Table
PA = PlayerAssign
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

    # 5) Each player should not be allocated to more than one table
    # --> already guaranteed by the dictionary structure

    return 0


def check_solution(parseInfo: ParseInfo, solution: Solution, rankDiff: Optional[int] = None) -> bool:
    return (_check_solution(parseInfo, solution, rankDiff) == 0)


def test_check_solution() -> None:
    parseInfo = {"toto": PI(0., [False, True]), "titi": PI(0., [False, True]), "tata": PI(0., [False, True]), "lolo": PI(0., [True, True])}

    solution = {"toto": PA(1, 0), "titi": PA(1, 0), "tata": PA(1, 0), "lolo": PA(1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == 0) # success

    solution = {"toto": PA(1, 0), "tata": PA(1, 0), "lolo": PA(1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -1) # fail 1)

    solution = {"toto": PA(0, 0), "titi": PA(0, 0), "tata": PA(0, 0), "lolo": PA(0, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -2) # fail 2)

    parseInfo = {"toto": PI(0., [False, True]), "titi": PI(0., [False, True]), "tata": PI(0., [False, True])}
    solution = {"toto": PA(1, 0), "titi": PA(1, 0), "tata": PA(1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -3) # fail 3)

    parseInfo = {"toto": PI(10., [False, True]), "titi": PI(0., [False, True]), "tata": PI(0., [False, True]), "lolo": PI(0., [True, True])}
    solution = {"toto": PA(1, 0), "titi": PA(1, 0), "tata": PA(1, 0), "lolo": PA(1, 0)}
    assert(_check_solution(parseInfo, solution, 0) == -4) # fail 4)

    print("All good!")


def print_solution(solution: Solution) -> None:
    print(20*"#" + " solution " + 20*"#")
    tables : Dict[int, Tuple[Day, List[Name]]] = {}
    for player in solution:
        day, table = solution[player]
        if table not in tables:
            tables[table] = (day, [])
        tables[table][1].append(player)

    for table in tables:
        print("Table", table, "of day", tables[table][0])
        for player in tables[table][1]:
            print("\t", player)

## Heuristic to compute the solution.
#
# The principle is to follow a partial ordering of the players, and then try
# to form contiguous groups out of that ordering.
#
# This ordering is such that two properties are ensured:
# 1) Players of same rank are contiguous
# 2) Within each even rank, the Day 1 only players are at the top while the
#    Day 2 only players are at the bottom. For each odd rank, it's the opposite:
#    Day 1 players at the bottom, Day 2 players at the top.
#    These two days are selected at random so that no particular day is biased.
#
# Since we represent this partial ordering with a totally ordered list, we also
# insert randomness into each equivalence class.
#
# This alternation is to ease the group making of people of different ranks,
# when the numbers are not ideal to work with. It introduces a potential bias
# though: the players who select both days will have more probability to be
# found in a table of the same rank as them, than those who only select one day.
#
# Those who only select one day will sometimes find themselves in a table of higher
# rank, sometimes in lower rank, but since we select Day 1 and Day 2 randomly,
# normally this shouldn't introduce any significant bias.
#
# Also, this particular algorithm becomes irrelevant if more than 2 days are
# available.. While I think it could be generalized, right now it's not worth
# the trouble.
##

bothDays = -1
RankGroups = Dict[Rank, Dict[Union[Day,int], List[Name]]]

def construct_rank_groups(parseInfo: ParseInfo) -> RankGroups:
    rg: RankGroups = {}
    for player in parseInfo:
        score, da = parseInfo[player]
        rank = score_to_rank(score)
        if rank not in rg:
            rg[rank] = {}
            for day in [-1, 0, 1]:
                rg[rank][day] = []
        if da == [True, True]:
            rg[rank][-1].append(player)
        elif da == [True, False]:
            rg[rank][0].append(player)
        elif da == [False, True]:
            rg[rank][1].append(player)
    return rg


def randomize_rank_groups(rankGroups: RankGroups) -> None:
    for rank in rankGroups:
        for day in rankGroups[rank]:
            rng.shuffle(rankGroups[rank][day])
    return


def order_players(parseInfo: ParseInfo, day1: Day) -> List[Name]:
    rankGroups = construct_rank_groups(parseInfo)
    randomize_rank_groups(rankGroups)
    ordered = []
    for rank in sorted(rankGroups.keys(), reverse=True):
        ordered.extend(rankGroups[rank][day1])
        ordered.extend(rankGroups[rank][bothDays])
        ordered.extend(rankGroups[rank][1-day1])
        day1 = 1-day1
    return ordered


# Example: cut_by_four(11)
def cut_by_four(n: int) -> List[int]:
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


def contiguous_gather_fixed(parseInfo: ParseInfo, players: List[Name],
                            orderedSizes: Tuple[int, ...]) -> Optional[Solution]:
    solution = {}
    table = 0
    currentPlayerIndex = 0
    for tableSize in orderedSizes:
        tablePlayers = []
        tableDay = None
        for i in range(tableSize):
            player = players[currentPlayerIndex + i]
            # Checking/setting the day
            availableDays = get_days(parseInfo[player].daysOk)
            assert(0 < len(availableDays) <= 2)
            if tableDay is None:
                if len(availableDays) == 1:
                    tableDay = availableDays[0]
            else:
                if len(availableDays) == 1 and availableDays[0] != tableDay:
                    return None
            tablePlayers.append(player)

        # Randomizing the day if it wasn't set
        if tableDay is None:
            tableDay = rng.randint(0, 1)

        # Adding each player to the solution
        for player in tablePlayers:
            solution[player] = PA(tableDay, table)

        table += 1
        currentPlayerIndex += len(tablePlayers)
    return solution


def get_tables_average_ranks(parseInfo: ParseInfo,
                             solution: Solution) -> Dict[Table, float]:
    tableRanks: Dict[Table, List[Rank]] = {}
    for player in solution:
        table = solution[player].table
        if table not in tableRanks:
            tableRanks[table] = []
        tableRanks[table].append(score_to_rank(parseInfo[player].score))
    return {table:mean(tableRanks[table]) for table in tableRanks}


# Returns a vector of rank difference compared to the average rank of the table
def solution_score(parseInfo: ParseInfo, solution: Solution) -> List[float]:
    tablesAvgRanks = get_tables_average_ranks(parseInfo, solution)
    return [abs(score_to_rank(parseInfo[player].score)
                - tablesAvgRanks[solution[player].table])
            for player in solution]


def select_best_solution(parseInfo: ParseInfo,
                         solutions: List[Solution]) -> Optional[Solution]:
    bestScore = None
    bestSolution = None
    for solution in solutions:
        score = solution_score(parseInfo, solution)
        if bestScore is None or score < bestScore:
            bestScore = score
            bestSolution = solution
    return bestSolution


# Forms a solution by gathering from top to bottom.
# It tries one solution per permutation of sizes, then takes the best
def contiguous_gather(parseInfo: ParseInfo, players: List[Name],
                      sizes: List[int]) -> Optional[Solution]:
    computed: Set[Tuple[int, ...]] = set()
    solutions: List[Solution] = []
    for orderedSizes in permutations(sizes):
        if orderedSizes in computed:
            break
        solution = contiguous_gather_fixed(parseInfo, players, orderedSizes)
        computed.add(orderedSizes)
        if solution is None:
            continue
        solutions.append(solution)
    return select_best_solution(parseInfo, solutions)


##
# Last resort matchmaking. Just packs players based on their days, and splits
# the "both days" players randomly where there is still room
# Can still fail if there is no solution at all, in which case the matchmaking should
# be done manually by the organizer
##
def random_solution(parseInfo: ParseInfo) -> Optional[Solution]:
    solution: Solution = {}
    players = list(parseInfo.keys())
    rng.shuffle(players)
    tableSizes = cut_by_four(len(players))
    tables = [[[None] * tableSize, None] for tableSize in tableSizes]
    for player in players:
        for ti, table in enumerate(tables):
            slots, day = table
            attributedSlot = False
            if day is None or day in get_days(parseInfo[player].daysOk):
                for i, slot in enumerate(slots): # type: ignore
                    if slot == None:
                        tables[ti][0][i] = player # type: ignore
                        daysOk = get_days(parseInfo[player].daysOk)
                        assert(0 < len(daysOk) <= 2)
                        if len(daysOk) == 1:
                            tables[ti][1] = daysOk[0] # type: ignore
                        attributedSlot = True
                        break
            if attributedSlot:
                break

    for ti, table in enumerate(tables):
        slots, day = table
        if day is None:
            day = rng.randint(0, 1) # type: ignore
        for player in slots: # type: ignore
            if player is None:
                return None
            else:
                solution[player] = PA(day, ti)

    return solution


# Sort by score, randomizing players of equal score
def partial_sort_score(parseInfo: ParseInfo) -> List[Name]:
    return []


# Returns whether a table is compatible in regards to the days
def table_ok(parseInfo: ParseInfo, players: List[Name]) -> bool:
    return False


##
# Seek a player to swap in upId
# seek a swapping partner in downId, and swap them
# Continue the process as long as the table upId isn't ok
# Returns true if it actually managed to correctify the table
# /!\ Supposes the players in upId and downId are already sorted by score /!\
##
def seek_and_swap_players(parseInfo: ParseInfo, upId: Table, downId: Table,
                          tables: Dict[Table, List[Name]], reverse: bool = False) -> bool:
    swapPlayerFound = False
    while not (table_ok(parseInfo, tables[upId]) or swapPlayerFound):
        # Seeking upIdPlayer
        upIdDay = None
        upIdPlayer = None
        upIdPi = None
        for pi, player in enumerate(tables[upId]):
            days = get_days(parseInfo[player].daysOk)
            if len(days) == 1:
                if upIdDay is None:
                    upIdDay = days[0]
                elif upIdDay != days[0]:
                    upIdPlayer = player
                    upIdPi = pi
                    break
        assert(upIdPlayer is not None)

        # Seeking downIdPlayer
        swapPlayerFound = False
        iterPlayers = tables[downId]
        if reverse:
            iterPlayers = reversed(iterPlayers)
        for pi, player in enumerate(iterPlayers):
            days = get_days(parseInfo[player].daysOk)
            if len(days) == 2 or (len(days) == 1 and days[0] != upIdDay):
                # do the swap
                tables[upId][upIdPi] = player
                tables[downId][pi] = upIdPlayer
                swapPlayerFound = True
                break

    return table_ok(parseInfo, tables[upId])


def deduce_day(parseInfo: ParseInfo, players: List[Name]) -> Optional[Day]:
    return None


##
# 1) Construct a first solution irrespective of the day constraint.
#    -> order by score, then pick groups from top to bottom
# 2) Perform swaps in order to correctify the solution
##
def group_and_swap_solution(parseInfo: ParseInfo) -> Optional[Solution]:
    tables: Dict[Table, List[Name]] = {}
    groupSizes = sorted(cut_by_four(len(parseInfo.keys())))
    players = partial_sort_score(parseInfo)
    tableIndex = 0
    playerIndex = 0
    for groupSize in groupSizes:
        tables[tableIndex] = players[playerIndex:playerIndex+groupSize]
        playerIndex += groupSize
        tableIndex += 1

    for i in range(tableIndex-1):
        if not table_ok(parseInfo, tables[i]):
            seek_and_swap_players(parseInfo, i, i+1, tables)

    # Reverse pass
    for i in reversed(range(1, tableIndex)):
        if not table_ok(parseInfo, tables[i]):
            success = seek_and_swap_players(parseInfo, i, i-1, tables, reverse=True)
            if not success:
                return None

    if not table_ok(parseInfo, tables[0]):
        return None

    solution = {}
    for i in tables:
        tablePlayers = tables[i]
        day = deduce_day(parseInfo, tablePlayers)
        assert(day is not None)
        for player in tablePlayers:
            solution[player] = PA(day, i)

    return solution


##
# Attempts a solution with a random day as "top day"
# If no solution was found, try the other day
# If still no solution, call the random_solution which just randomizes
# regardless of score
##
def compute_solution(parseInfo: ParseInfo) -> Optional[Solution]:
    day1 = rng.randint(0, 1)
    ordered = order_players(parseInfo, day1)
    group_sizes = cut_by_four(len(ordered))
    solution = contiguous_gather(parseInfo, ordered, group_sizes)
    if solution is None:
        ordered2 = order_players(parseInfo, 1-day1)
        solution = contiguous_gather(parseInfo, ordered2, group_sizes)
    if solution is None:
        print("Smart contiguous_gather failed, returning a random solution instead")
        solution = random_solution(parseInfo)
    return solution


parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

if args.file == "test":
    test_check_solution()
    sys.exit(0)

with open(args.file, 'r') as f:
    parseInfo = parse_file(f)

# Some debug prints
print({player: parseInfo[player].score for player in parseInfo})
day1Only = [player for player in parseInfo if parseInfo[player].daysOk == [True, False]]
day2Only = [player for player in parseInfo if parseInfo[player].daysOk == [False, True]]
day12 = [player for player in parseInfo if parseInfo[player].daysOk == [True, True]]
print("day1 only:", day1Only)
print("day2 only:", day2Only)
print("both days:", day12)
print(80*"-")

solution = compute_solution(parseInfo)
if solution is None:
    print("No fitting solution could be found.")
else:
    print_solution(solution)
    if not check_solution(parseInfo, solution):
        print("/!\\ The solution is not valid /!\\")

