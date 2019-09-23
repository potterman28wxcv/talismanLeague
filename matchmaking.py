#!/usr/bin/python3.6
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

print(args.file)
