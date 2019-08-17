#!/usr/bin/env python
"""This script calculates the Mean Average Precision (MAP) measure for a TREC-CAR run file."""
import shutil

__author__ = "Shubham Chatterjee"
__version__ = "8/16/19"

from typing import Dict, List
import sys
import os
import argparse
from map import mean_avg_prec, get_rankings
import operator


def find_best_runs(run_dir: str, bestdir: str, qrel_file: str):
    run_file_list = os.listdir(run_dir)
    map_dict: Dict[str, float] = {}
    qrel_file_dict = get_rankings(qrel_file)

    print("Finding top 10 runs...")

    # Find MAP for each file
    for file_name in run_file_list:
        full_file_name = os.path.join(run_dir, file_name)
        run_file_dict = get_rankings(full_file_name)
        _map, p_dict = mean_avg_prec(run_file_dict, qrel_file_dict)
        map_dict[file_name] = _map
    print("[Done].")

    i: int = 0

    print("Copying best runs to dir...")

    for key, value in sorted(map_dict.items(), key=operator.itemgetter(1), reverse=True):
        i = i + 1
        print(key + " " + str(value))
        full_file_name = os.path.join(run_dir, key)
        copy(full_file_name, bestdir)
        if i == 10:
            break

    print("[Done].")


def copy(file, dir):
    shutil.copy(file, dir)


def main():
    parser = argparse.ArgumentParser("This script finds the best runs in terms of MAP.")
    parser.add_argument("--rundir", help="Path to the directory containing runs.", required=True)
    parser.add_argument("--bestdir", help="Path to the directory to put the best runs.", required=True)
    parser.add_argument("--qrel", help="Path to the ground truth (qrel) file.", required=True)
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    find_best_runs(args.rundir, args.bestdir, args.qrel)


if __name__ == '__main__':
    main()


