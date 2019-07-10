#!/usr/bin/env python
"""This script creates a new TREC-CAR run file using a RankLib feature file and the RankLib model file."""

__author__ = "Shubham Chatterjee"
__version__ = "6/6/19"

from typing import Dict, List
from collections import OrderedDict
import sys
import argparse
import os


def get_weights(model_file: str) -> Dict[str, float]:
    weights: Dict[str, float] = {}
    with open(model_file, 'r') as f:
        for line in f:
            if not line.startswith('#'):
                data = line.split(" ")
                for val in data:
                    f = val.split(":")[0]
                    w = float(val.split(":")[1])
                    weights[f] = w
    return weights


def get_scores(feature_file: str, weights: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    score_map: OrderedDict[str, OrderedDict[str, float]] = OrderedDict()
    _map: OrderedDict[str, float]
    with open(feature_file, 'r') as f:
        for line in f:
            sum_score: float = 0.0
            line_parts = line.split(" ")
            query_id: str = line_parts[len(line_parts) - 1].split("_")[0][1:]
            para_id: str = line_parts[len(line_parts) - 1].split("_")[1]

            """
            # For every (feature, value pair do
            # Note: line_parts[0] --> target, line_parts[1] --> qid, line_parts[2]..line_parts[len(line_parts) - 1] --> (feature : score) pairs
            # This is according to the RankLib feature file format
            """
            n: int = len(line_parts) - 1
            for i in range(2, n):
                feature: str = line_parts[i].split(":")[0]
                weight: float = weights[feature]
                score: float = float(line_parts[i].split(":")[1])
                new_score: float = weight * score
                sum_score += new_score

            """
            # If the score_map already contains the query, then get the map of (para_id, score) for the query
            # Otherwise make a new dictionary of (para_id, score) for the query
            """
            if query_id in score_map.keys():
                _map = score_map[query_id]
            else:
                _map = OrderedDict()

            """Put the (para_id, score) values in the map"""
            _map[para_id] = sum_score
            score_map[query_id] = _map
    return score_map


def sort_by_value_descending(dictionary) -> Dict[str, float]:
    return OrderedDict(sorted(dictionary.items(), key=lambda kv: (kv[1], kv[0]), reverse=True))


def make_run_strings(score_map: Dict[str, Dict[str, float]]) -> List[str]:
    run_strings: List[str] = []
    for query_id in score_map.keys():
        rank = 0
        _map = sort_by_value_descending(score_map[query_id])
        for para_id in _map.keys():
            score = _map[para_id]
            if score != 0:
                run_file_string = query_id + " Q0 " + para_id.rstrip() + " " + str(rank) + " " + str(score) + " " + "combined"
                run_strings.append(run_file_string)
                rank += 1

    return run_strings


def combine(feature_file: str, model_file: str, combined_file: str):
    print("Reading model file. Getting feature weights....", end=' ')
    weights: Dict[str, float] = get_weights(model_file)
    print("[Done]")
    print("The weight vector is {}".format(weights))
    print("Reading feature file. Getting scores for each feature....", end=' ')
    score_map: Dict[str, Dict[str, float]] = get_scores(feature_file, weights)
    print("[Done]")
    run_strings: List[str] = make_run_strings(score_map)
    print("Writing to file....", end=" ")
    write_file(run_strings, combined_file)
    print("[Done]")
    print("Combined run file written to: " + combined_file)


def write_file(run_strings: List[str], combined_file: str):
    with open(combined_file, 'w') as file:
        for run_file_string in run_strings:
            file.write(run_file_string + os.linesep)


def main():
    parser = argparse.ArgumentParser("Create a new trec_eval compatible TREC-CAR run file using the RankLib model.")
    parser.add_argument("--feature", help="Path to the RankLib feature file", required=True)
    parser.add_argument("--model", help="Path to the RankLib model file", required=True)
    parser.add_argument("--combined", help="Path to the combined run file", required=True)
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    combine(args.feature, args.model, args.combined)


if __name__ == '__main__':
    main()
