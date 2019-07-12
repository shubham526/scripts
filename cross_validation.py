#!/usr/bin/env python
"""This script takes a directory of TREC-CAR run files and does k- fold cross-validation."""

__author__ = "Shubham Chatterjee"
__version__ = "7/11/19"

from collections import deque
import sys
import argparse
import os
import shutil
import combine
import create_feature_file
import create_folds
import rank_lib_runner
import re


def main():
    parser = argparse.ArgumentParser("Do Cross-Validation on TREC-CAR run files.")
    parser.add_argument("--cvdir", help="Path to the directory where all CV data will be stored.", required=True)
    parser.add_argument("--rundir", help="Path to the directory containing the run files.", required=True)
    parser.add_argument("--qrelsdir", help="Path to the directory containing the ground truth files.", required=True)
    parser.add_argument("--qrelfile", help="Name of the ground truth file file.", required=True)
    parser.add_argument("--zscore", help="Whether to zscore normalize the features or not. "
                                         "Defaults to no normalization.", action="store_true")
    parser.add_argument("--k", help="Number of folds required.",
                        required=True)
    parser.add_argument("--ranklib", help="Path to the RankLib JAR file. ")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    cross_validation(args.cvdir, args.rundir, args.qrelsdir, args.qrelfile, args.zscore, int(args.k), args.ranklib)


def cross_validation(cv_dir, run_dir, qrels_dir, qrel_file, zscore, k, ranklib_path):
    feature_dir = cv_dir + "/" + "features"
    fold_dir = cv_dir + "/" + "folds"
    model_dir = cv_dir + "/" + "models"
    train_dir = cv_dir + "/" + "train"
    test_dir = cv_dir + "/" + "test"
    comb_dir = cv_dir + "/" + "combined"

    print("Creating directories.......")
    print("============================================================================")

    # Create directories within the CV directory to hold different things
    create_directory(feature_dir)
    create_directory(fold_dir)
    create_directory(train_dir)
    create_directory(test_dir)

    if ranklib_path:
        create_directory(model_dir)
        create_directory(comb_dir)

    print("\n")

    print("Copying run files to CV directory.......")
    print("============================================================================")

    # Copy run files to CV directory
    copy(run_dir, feature_dir)

    print("\n")

    print("Creating folds.......")
    print("============================================================================")

    # Divide the runfiles into folds
    create_folds.create_folds(fold_dir, feature_dir, k)

    print("\n")

    print("Creating test data.......")
    print("============================================================================")

    # Create test data
    create_test_set(fold_dir, test_dir, qrels_dir, qrel_file, zscore, k)

    print("\n")

    print("Creating train data.......")
    print("============================================================================")

    # Create train data
    create_train_set(train_dir, test_dir, k)

    print("\n")

    if ranklib_path:
        ranklib(train_dir, model_dir, comb_dir, ranklib_path, k)
    print("Done.")
    print("============================================================================")


def ranklib(train_dir, model_dir, comb_dir, ranklib_path, k):
    print("Running RankLib with Coordinate Ascent, optimized for MAP.......")
    print("============================================================================")

    # Run RankLib with Coordinate Ascent, optimize for Mean Average Precision (MAP) on each train file
    train_files = os.listdir(train_dir)
    for file_name in train_files:
        full_file_name = os.path.join(train_dir, file_name)
        n = [int(s) for s in re.findall(r'\d+', file_name)][0]  # Find the fold number
        model_file = model_dir + "/model-" + str(n) + ".txt"
        rank_lib_runner.run(ranklib_path, full_file_name, model_file)

    print("\n")

    print("Combining models to get final trec_eval compatible run file.......")
    print("============================================================================")

    # Combine the models with the feature files
    model_files = os.listdir(model_dir)
    for i in range(len(model_files)):
        model = model_files[i]
        feature = train_files[i]
        n = [int(s) for s in re.findall(r'\d+', model)][0]  # Find the fold number
        combined = comb_dir + "/comb-" + str(n) + ".txt"
        combine.combine(feature, model, combined)

    # Concatenate all combined files to get one big ranklib combined file
    comb_files = os.listdir(comb_dir)
    l = []
    for file_name in comb_files:
        full_file_name = os.path.join(comb_dir, file_name)
        l.append(full_file_name)
    final_combined_file = comb_dir + "/ranklib-combined-" + str(k) + "-fold-cross-validated-file.run"
    concat(l, final_combined_file)


def create_directory(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed. Directory already present." % path)
    else:
        print("Successfully created the directory %s " % path)


def copy(src, dest):
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dest)


def grouper(iterable, elements, rotations):
    """
    In order to get a cyclic elements from your list you can use deque from collections module and do a deque.rotation(-1).
    :param iterable: the list to iterate over
    :param elements: how many elements to pick from the list?
    :param rotations: how many cycles do you need?
    :return: empty list if the number of elements to pick is greater than size of list
    """
    if elements > len(iterable):
        return []

    b = deque(iterable)
    for _ in range(rotations):
        yield list(b)[:elements]
        b.rotate(-1)


def get_leave(full_list, lst):
    return list(set(full_list) - set(lst))[0]


def concat(file_list, out_file):
    with open(out_file, 'wb') as out:
        for file in file_list:
            with open(file, 'rb') as f:
                shutil.copyfileobj(f, out)


def create_test_set(fold_dir, test_dir, qrels_dir, qrel_file, zscore, k):
    for i in range(0, k):
        fdir = fold_dir + "/fold-" + str(i)
        feature_file_name = "feature-file-" + str(i) + ".txt"
        create_feature_file.create_feature_file(fdir, qrels_dir, qrel_file, test_dir, feature_file_name, zscore)


def create_train_set(train_dir, test_dir, k):
    # Generate a list of all possible feature file numbers
    file_list = [i for i in range(0, k)]

    # Get a list of all possible cyclical combinations of the list, picking k - 1 elements for k cycles
    cycle = list(grouper(file_list, k - 1, k))

    # For every list in the cycle
    for l in cycle:

        # Get the leave number and make the leave file name
        leave = get_leave(file_list, l)
        leave_file = train_dir + "/leave-" + str(leave) + ".txt"
        files = []

        # For every file number in the list
        for n in l:
            # Make a list of feature files to concatenate
            feature_file = test_dir + "/feature-file-" + str(n) + ".txt"
            files.append(feature_file)

        # Concatenate those files
        concat(files, leave_file)


if __name__ == '__main__':
    main()