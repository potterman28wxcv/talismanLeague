#!/usr/bin/python3.6
import argparse
from typing import *

class PlayerInfo:
  def __init__(self, score: int, daysOk: List[bool]):
    self.score = score
    self.daysOk = daysOk

Name = str
ParseInfo = Dict[Name, PlayerInfo]
def parse (filename: str) -> ParseInfo:
  return {}

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

print(parse(args.file))
