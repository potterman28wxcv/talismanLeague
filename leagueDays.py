#!/usr/bin/python3.6
from typing import List, Dict, Tuple, Optional, Set

Player=int
Day=int
PlayerInfos = Dict[Player, Optional[List[Day]]]

playerInfos : PlayerInfos = {
  1: [1, 2, 3, 4],
  2: [1, 3, 5],
  3: [1, 2, 3, 4, 5],
  4: [4],
  5: [1, 3, 5],
  6: [1, 2, 3, 4],
  7: [1, 2, 3, 4, 5],
  8: [1, 2, 3, 4, 5],
  9: [1, 2, 3, 4],
  10: [5],
  11: [1, 3, 4, 5],
  12: [5],
  13: [1, 5],
  14: [1],
  15: [3],
  16: [2, 4],
  17: [2, 4],
  18: [1, 3],
  19: [1, 3, 4, 5],
  20: [2, 3, 4, 5],
  21: [2],
  22: [1, 2, 3],
  23: [1, 3, 5],
  24: [3, 4],
  25: [1, 3, 5],
  26: None, # could not befriend them (got blocked on steam)
  27: [1, 2, 3, 4, 5],
  28: None, # could not befriend them yet (friend invite not accepted)
  29: [1, 5],
  30: [1, 3, 4, 5]
}

DayInfos = Dict[Day, Set[Player]]
def gen_day_infos () -> DayInfos:
  dayInfos : DayInfos = {}
  for player, days in playerInfos.items():
    if days is None:
      continue
    for day in days:
      if day not in dayInfos:
        dayInfos[day] = set([])
      dayInfos[day].add(player)
  return dayInfos

Choice=Tuple[Day, Day]
Score=int
def choice_from_day_infos (dayInfos: DayInfos) -> Dict[Choice, Score]:
  players : Set[Player] = set(playerInfos.keys())
  scores : Dict[Choice, Score] = {}
  for day1 in dayInfos:
    for day2 in dayInfos:
      if day2 <= day1:
        continue
      playersWhoCan = dayInfos[day1].union(dayInfos[day2])
      playersWhoCannot = players - playersWhoCan
      choice = (day1, day2)
      print("Choice: ", choice, ", playersWhoCannot: ", playersWhoCannot)
      scores[choice] = len(playersWhoCan)
  return scores

dayInfos = gen_day_infos()
scores = choice_from_day_infos(dayInfos)
print(scores)
