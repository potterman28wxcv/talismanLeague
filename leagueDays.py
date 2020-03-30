from typing import List, Dict, Tuple, Optional, Set

Player=int
Day=int
PlayerInfos = Dict[Player, Optional[List[Day]]]

rawPlayerInfos : PlayerInfos = {
  1:  [1, 2, 3, 4, 5, 6, 7],
  2:  [   2, 3, 4, 5, 6, 7],
  3:  [1,             6, 7],
  4:  [1,          5, 6   ],
  5:  [1, 2, 3, 4, 5, 6, 7],
  6:  [1, 2, 3, 4, 5      ],
  7:  [1,       4         ],
  8:  [1,       4,       7],
  9:  [      3, 4,    6, 7],
  10: [   2, 3,    5, 6   ],
  11: [1, 2, 3, 4, 5, 6, 7],
  12: [   2, 3, 4, 5, 6, 7],
  13: [   2,       5      ],
  14: [1,       4,       7],
  15: [      3, 4,    6, 7],
  16: [1,    3, 4,    6, 7],
  17: [         4         ],
  18: [         4,       7],
  19: [1, 2, 3, 4, 5, 6, 7],
  20: [1,       4, 5, 6, 7],
  21: [1,                7],
  22: [                  7],
  23: [                  7],
  24: [                  7],
  25: [            5, 6   ],
  26: [1,       4,       7],
  27: [1,       4,       7],
  28: [   2, 3,    5, 6   ],
  29: [1,    3, 4,    6, 7],
  30: [1, 2, 3, 4, 5, 6, 7],
  31: [         4,    6   ],
  32: [1, 2, 3, 4         ],
  33: [   2, 3, 4         ],
  34: [   2,          6   ],
  35: [1,       4         ],
  36: [      3,       6   ],
  37: [1,       4,       7],
  38: [1,             6, 7],
  39: [1,       4, 5,    7],
  40: [            5, 6, 7]
}

playerInfos = {key:val for key, val in rawPlayerInfos.items() if val is not None}

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
