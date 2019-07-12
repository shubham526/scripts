#!/usr/bin/env python
"""This script divides a TREC-CAR run file into folds for cross-validation."""

__author__ = "Shubham Chatterjee"
__version__ = "6/7/19"

import argparse
import sys
import os


def cross_validation_split(run_file_path, dest, folds):
    run_file_name = run_file_path[run_file_path.rfind("/")+1:]
    print("File: " + run_file_name)
    query_list = get_query_list(run_file_path)

    for i in range(0, int(folds)):
        fold_query_list = split(query_list, folds)[i]
        fold_file_name = "fold_" + str(i) + "_" + run_file_name
        fold_dir = dest + "/" + "fold-" + str(i)
        if not os.path.isdir(fold_dir):
            create_directory(fold_dir)
        create_fold(fold_query_list, fold_file_name, run_file_path, fold_dir)


def create_directory(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)


def create_fold(fold_query_list, fold_file_name, run_file_path, fold_dir):
    fold_file_path = fold_dir + "/" + fold_file_name
    run_strings = []
    with open(run_file_path, 'r') as f:
        for line in f:
            line_parts = line.split(" ")
            query = line_parts[0]
            query_id = query.split("+")[0]
            if query_id in fold_query_list:
                run_strings.append(line.rstrip())
    write_file(fold_file_path, run_strings)


def split(query_list, n):
    return [query_list[i::n] for i in range(n)]


def get_query_list(run_file_path):
    query_list = []
    with open(run_file_path, 'r') as f:
        for line in f:
            line_parts = line.split(" ")
            query = line_parts[0]
            query_id = query.split("+")[0]
            if query_id not in query_list:
                query_list.append(query_id)
    return query_list


def write_file(file_path, run_strings):
    with open(file_path, 'w') as file:
        for run_file_string in run_strings:
            file.write(run_file_string + "\n")


def main():
    parser = argparse.ArgumentParser("Divide a TREC-CAR run file into folds for cross-validation.")
    parser.add_argument("--file", help="Path to the data file to split.", required=True)
    parser.add_argument("--save", help="Path to the directory where the folds will be saved.", required=True)
    parser.add_argument("--fold", help="Number of folds required.", required=True)
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    cross_validation_split(args.file, args.save, int(args.fold))


if __name__ == '__main__':
    main()
