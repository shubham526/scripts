#!/usr/bin/env python
"""This script runs the RankLib JAR with Coordinate Ascent, optimized for Mean Average Precision."""
import argparse

__author__ = "Shubham Chatterjee"
__version__ = "4/14/20"

import subprocess as sp
import os
import sys


def run(rlib_path, feature_file, model_file, metric):
    if not os.path.exists(feature_file):
        print("Feature file does not exist.")
        sys.exit(-1)

    rlib_command = 'java -jar {} -train {} -ranker 4 -metric2t {} -save {}'.format(rlib_path, feature_file,
                                                                                   metric, model_file)
    process = sp.Popen(rlib_command.split(), stdout=sp.PIPE)
    for line in process.stdout:
        sys.stdout.write(line.decode('utf-8'))
    exitcode = process.wait()
    if exitcode == 0:
        print("Sub process exited gracefully")
    else:
        print("RankLib process did not exit gracefully, exiting the program")
        sys.exit(-1)


def main():
    parser = argparse.ArgumentParser("Run RankLib with Coordinate Ascent, optimized for Mean Average Precision.")
    parser.add_argument("--jar", help="Path to the RankLib JAR file.", required=True)
    parser.add_argument("--feature", help="Path to the RankLib compatible feature file (training data).", required=True)
    parser.add_argument("--model", help="Path to the model file.", required=True)
    parser.add_argument("--metric", help="Metric to optimize for (MAP|NDCG@k|DCG@k|P@k|RR@k|ERR@k)", required=True)
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    run(args.jar, args.feature, args.model, args.metric)


if __name__ == '__main__':
    main()