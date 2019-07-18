#!/usr/bin/env python
"""This script calculates the standard error for a trec_eval file obtained using the  -q option."""
__author__ = "Shubham Chatterjee"
__version__ = "6/6/19"

import statistics
import math
import sys
import argparse
from typing import List


def standard_error(file_path: str, qrel_file_path: str) -> float:
    nums: List[float] = []
    n: int = number_of_queries(qrel_file_path)
    with open(file_path, 'r') as file:
        for line in file:
            m = line.split()
            nums.append(float(m[2]))

    return statistics.stdev(nums[0:len(nums)]) / math.sqrt(n)


def number_of_queries(qrel_file_path: str) -> int:
    query_list: List[str] = []
    with open(qrel_file_path, 'r') as file:
        for line in file:
            line_parts = line.split(" ")
            query_id = line_parts[0]
            if query_id not in query_list:
                query_list.append(query_id)
    return len(query_list)


def main():
    parser = argparse.ArgumentParser("Calculate standard error for a TREC-CAR run file")
    parser.add_argument("-f", "--filepath", help="Path to the trec_eval file (obtained using -q option)", required=True)
    parser.add_argument("-q", "--qrelpath", help="Path to the ground truth (qrel) file", required=True)
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    p = standard_error(args.filepath, args.qrelpath)
    print("SE = " + str(p))


if __name__ == '__main__':
    main()

