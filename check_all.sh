#!/bin/bash

for program in $(ls *.py); do
  echo "Checking $program.."
  mypy $program
done
