#!/usr/bin/env python
"""This script calculates the Mean Average Precision (MAP) measure for a TREC-CAR run file."""
__author__ = "Shubham Chatterjee"
__version__ = "8/16/19"

from typing import Dict, List
import sys
import argparse
from map import mean_avg_prec


def main():
    parser = argparse.ArgumentParser("This script finds the best runs in terms of MAP.")
    parser.add_argument("--filepath", help="Path to the run file.", required=True)
    parser.add_argument("--qrelpath", help="Path to the ground truth (qrel) file.", required=True)
    parser.add_argument("--q", help="Whether per query or not. Default is False.",  action="store_true")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    p, prec_dict = mean_avg_prec(args.filepath, args.qrelpath)

    if args.q:
        for queryID in prec_dict:
            mean_avg_precision = prec_dict[queryID]
            print_string = "map" + "\t\t\t" + queryID + "\t" + "{:.4f}".format(mean_avg_precision)
            print(print_string)

    print("map" + "\t\t\t" + "all" + "\t" + "{:.4f}".format(p))


if __name__ == '__main__':
    main()