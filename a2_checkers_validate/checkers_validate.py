import copy
import random
import time
import queue
import sys
import os
from queue import PriorityQueue

# Validation script for CSC384 A2 : checkers.py
# Change input2.txt, output2.txt and solution2.txt to run
#    other test inputs.

if __name__ == '__main__':
  # Invoke the shell command to test the checkers solver
  print("Input file: input2.txt, output file: output2.txt")
  os.system("python3 checkers.py input2.txt output2.txt")

  output_read = open("output2.txt", "r")
  solution_read = open("solution2.txt", "r")

  output_lines = output_read.readlines()
  solution_lines = solution_read.readlines()
  passed = True

  for index in range(1, len(output_lines)):
    if output_lines[index].strip() != solution_lines[index].strip():
      print(f"Line {index + 1}: "
                             f"Expected <{output_lines[index].strip()}> "
                             f"Encountered <{solution_lines[index].strip()}>\n")
      passed = False
      break

  print("Checkers output matches solution file.")
