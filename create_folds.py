#!/usr/bin/env python
"""This script takes a directory of TREC-CAR run files and divides each of them into folds for cross-validation."""

__author__ = "Shubham Chatterjee"
__version__ = "7/11/19"

import sys
import argparse
import os
import cross_validation_split


def main():
    parser = argparse.ArgumentParser("Create folds for TREC-CAR run files in a directory.")
    parser.add_argument("--fdir", help="Path to the directory where the folds will be saved.", required=True)
    parser.add_argument("--rdir", help="Path to the directory containing the run files.", required=True)
    parser.add_argument("--fold", help="Number of folds required.", required=True)
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    create_folds(args.fdir, args.rdir, int(args.fold))


def create_folds(fold_dir, run_dir, fold):
    src_files = os.listdir(run_dir)
    for file_name in src_files:
        full_file_name = os.path.join(run_dir, file_name)
        if os.path.isfile(full_file_name):
            cross_validation_split.cross_validation_split(full_file_name, fold_dir, fold)


if __name__ == '__main__':
    main()
