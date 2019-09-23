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
        name = ''.join(words[0:-3])
        score = float(words[-3])
        daysOk = [bool(words[-2]), bool(words[-1])]

        assert(name not in parseInfo)
        parseInfo[name] = (score, daysOk)
    return parseInfo


parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

with open(args.file, 'r') as f:
    parseInfos = parse_file(f)

print(parseInfos)
