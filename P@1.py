#!/usr/bin/env python
"""This script calculates the Precision at 1 measure for a TREC-CAR run file."""
__author__ = "Shubham Chatterjee"
__version__ = "6/6/19"

from typing import Dict, List
import sys
import argparse


def p_at_1(run_file: str, qrel_file: str):
    run_file_dict = get_rankings(run_file)
    qrel_file_dict = get_rankings(qrel_file)
    prec_dict: Dict[str, int] = {}
    s: int = 0

    for queryID in run_file_dict:
        ret_para_list = run_file_dict[queryID]
        rel_para_list = qrel_file_dict[queryID]

        if len(rel_para_list) != 0:
            if ret_para_list[0] in rel_para_list:
                prec_dict[queryID] = 1
            else:
                prec_dict[queryID] = 0
        else:
            print("Did not find ground truth for query: " + queryID)

    for i in prec_dict.values():
        s += i

    avg_p_at_1 = s / len(prec_dict)
    return avg_p_at_1, prec_dict


def get_rankings(file_path: str) -> Dict[str, List[str]]:
    rankings: Dict[str, List[str]] = {}
    with open(file_path, 'r') as file:
        for line in file:
            line_parts = line.split(" ")
            queryID = line_parts[0]
            field2 = line_parts[2]
            _list: List[str] = []
            if queryID in rankings.keys():
                _list = rankings[queryID]
            _list.append(field2)
            rankings[queryID] = _list
    return rankings


def main():
    parser = argparse.ArgumentParser("Calculate Precision at 1 for a TREC-CAR run file")
    parser.add_argument("--filepath", help="Path to the run file.", required=True)
    parser.add_argument("--qrelpath", help="Path to the ground truth (qrel) file.", required=True)
    parser.add_argument("--q", help="Whether per query or not. Default is False.",  action="store_true")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    p, prec_dict = p_at_1(args.filepath, args.qrelpath)

    if args.q:
        for queryID in prec_dict:
            p_at_one = prec_dict[queryID]
            print_string = "P@1" + "\t\t\t" + queryID + "\t" + str(p_at_one)
            print(print_string)

    print("P@1" + "\t\t\t" + "all" + "\t" + str(p))


if __name__ == '__main__':
    main()
























