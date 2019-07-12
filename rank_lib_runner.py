#!/usr/bin/env python
"""This script runs the RankLib JAR with Coordinate Ascent, optimized for Mean Average Precision."""

__author__ = "Shubham Chatterjee"
__version__ = "7/11/19"

import subprocess as sp
import os
import sys


def run(rlib_path, feature_file, model_file):
    if not os.path.exists(feature_file):
        print("Feature file does not exist.")
        sys.exit(-1)

    rlib_command = 'java -jar {} -train {} -ranker 4 -metric2t MAP -save {}'.format(rlib_path, feature_file, model_file)
    process = sp.Popen(rlib_command.split(), stdout=sp.PIPE)
    for line in process.stdout:
        sys.stdout.write(line.decode('utf-8'))
    exitcode = process.wait()
    if exitcode == 0:
        print("Sub process exited gracefully")
    else:
        print("RankLib process did not exit gracefully, exiting the program")
        sys.exit(-1)