import argparse
from typing import List, Optional

parser = argparse.ArgumentParser()
parser.add_argument("scorefile")
args = parser.parse_args()

class LineReader:
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.index = 0

    def peek(self) -> Optional[str]:
        if not self.endReached:
            return self.lines[self.index]
        else:
            return None

    def consume(self) -> str:
        assert not self.endReached
        self.index += 1
        return self.lines[self.index - 1]

    @property
    def endReached(self) -> bool:
        return (self.index == len(self.lines))


class ScoreEntry:
    def __init__(self, player: str, faction: str, character: str, score: str,
            gain: str, bonus: str, newScore: str):
        self.player = player
        self.faction = faction
        self.character = character
        self.score = float(score)
        self.gain = float(gain)
        self.bonus = float(bonus)
        self.newScore = float(newScore)


def get_header(lineReader: LineReader) -> str:
    header = lineReader.consume()
    return header.split('\t')[0]


def sort_entries(scoreEntries: List[ScoreEntry]) -> None:
    scoreEntries.sort(key = lambda x: x.gain, reverse=True)


def ordinal_position(i: int) -> str:
    assert i > 0
    assert i in range(1, 7), "Too many players in the table"
    ordinals = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th"}
    return ordinals[i]


def print_table(tableName: str, scoreEntries: List[ScoreEntry]) -> None:
    print("[b]{}:[/b]".format(tableName))
    print("[list]")
    for i,entry in enumerate(scoreEntries):
        pos = ordinal_position(i+1)
        name = entry.player
        char = entry.character
        gain = entry.gain
        bonus = entry.bonus
        tgain = gain + bonus
        score = entry.score
        nscore = entry.newScore
        assert nscore == tgain+score, "Wrong score written in the spreadsheet!"
        print("[*]{pos}) {name} with {char} gains {tgain} ({gain} + {bonus}). New score: {score} + {tgain} = {nscore}"
            .format(pos=pos, name=name, char=char, tgain=tgain, gain=gain,
                bonus=bonus, score=score, nscore=nscore))
    print("[/list]")
    print("")


def process_table(lineReader: LineReader) -> None:
    scoreEntries = []
    tableName = get_header(lineReader)
    while True:
        entryLine = lineReader.peek()
        if entryLine is None:
            break
        split = entryLine.split('\t')
        if not split[0].startswith("Table"):
            subsplit = split[1:8]
            scoreEntry = ScoreEntry(*subsplit)
            scoreEntries.append(scoreEntry)
            lineReader.consume()
        else:
            break
    sort_entries(scoreEntries)
    print_table(tableName, scoreEntries)


lines = open(args.scorefile).read().splitlines()
lineReader = LineReader(lines)

while not lineReader.endReached:
    process_table(lineReader)
