#!/usr/bin/env python
"""This script creates a RankLib compatible feature file."""

__author__ = "Shubham Chatterjee"
__version__ = "7/9/19"

import argparse
import sys
import os
import pandas as pd
import numpy as np
from scipy.stats import zscore
from typing import List, Dict


def read_run_files(run_dir: str):

    runfiles: Dict[str, Dict[str, Dict[str, float]]] = {}
    list_of_runfiles: List[str] = sorted(os.listdir(run_dir))
    for fname in list_of_runfiles:
        print(fname)
        rankings: Dict[str, Dict[str, float]] = {}
        with open(run_dir + "/" + fname) as f:
            for line in f:
                line_elems = line.split()
                query = line_elems[0]
                para = line_elems[2]
                runscore = float(line_elems[4])
                if query in rankings.keys():
                    rankings[query][para] = runscore
                else:
                    para_score_dict = {para: runscore}
                    rankings[query] = para_score_dict
        runfiles[fname] = rankings
        f.close()
    return runfiles


def read_ground_truth_file(qrels_dir: str, qrels_file: str):
    qrels_dict: Dict[str, List[str]] = {}
    with open(qrels_dir + "/" + qrels_file, 'r') as f:
        for line in f:
            query = line.split()[0]
            para = line.split()[2]
            if query in qrels_dict.keys():
                qrels_dict[query].append(para)
            else:
                para_list: List[str] = [para]
                qrels_dict[query] = para_list
    f.close()
    return qrels_dict


def create_pool(run_dir: str):
    pool: Dict[str, List[str]] = {}
    list_of_runfiles: List[str] = sorted(os.listdir(run_dir))
    for fname in list_of_runfiles:
        with open(run_dir + "/" + fname) as f:
            for line in f:
                line_elems = line.split()
                query = line_elems[0]
                para = line_elems[2]
                if query in pool.keys():
                    pool.get(query).append(para)
                else:
                    para_list: List[str] = [para]
                    pool[query] = para_list
    f.close()
    return pool


def create_feature_dict(runfiles, pool):
    features: Dict[str, Dict[str, Dict[int, float]]] = {}
    for query in pool.keys():
        para_list = pool[query]
        for para in para_list:
            get_feature_value(query, para, features, runfiles)

    return features


def get_feature_value(query, para, features, runfiles):
    fet_val_dict: Dict[int, float] = {}
    fet = 1
    for file in runfiles:
        rankings = runfiles[file]
        if query in rankings.keys():
            para_score_dict = rankings[query]
            if para in para_score_dict:
                fet_val_dict[fet] = para_score_dict[para]
            else:
                fet_val_dict[fet] = 0.0
        else:
            fet_val_dict[fet] = 0.0
        fet = fet + 1
    if query in features.keys():
        features[query][para] = fet_val_dict
    else:
        para_val_dict = {para: fet_val_dict}
        features[query] = para_val_dict


def make_feature_file(feature_dict, qrels):
    fet_line_list: List[str] = []
    qid: int = 1
    for query in feature_dict.keys():
        para_dict = feature_dict[query]
        rel_para_list = qrels[query]
        for para in para_dict.keys():
            fet_val_dict = para_dict[para]
            if para in rel_para_list:
                target = "1"
            else:
                target = "0"
            fet_line = target + " " + "qid:" + str(qid)
            for fet in fet_val_dict.keys():
                fet_line = fet_line + " " + str(fet) + ":" + str(fet_val_dict[fet])
            fet_line = fet_line + " #" + str(query) + "_" + str(para)
            fet_line_list.append(fet_line)
        qid = qid + 1
    return fet_line_list


def write_feature_file(fet_line_list, out_fet_file):
    with open(out_fet_file, 'w') as file:
        for fet_line in fet_line_list:
            file.write(fet_line + "\n")


def dict_to_dataframe(fet_dict):
    new_dict = {}

    for query in fet_dict.keys():
        para_dict = fet_dict[query]
        for para in para_dict.keys():
            q = query + "_" + para
            fet_val_dict = para_dict[para]
            new_dict[q] = fet_val_dict

    df = pd.DataFrame.from_dict(new_dict, orient='index').fillna(0)
    return df


def normalize_dataframe(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    normalized_df = df[numeric_cols].apply(zscore)
    return normalized_df


def convert(df_dict):
    norm_features = {}
    for key in df_dict.keys():
        query = key.split("_")[0]
        para = key.split("_")[1]
        fet_val_dict = df_dict[key]
        if query in norm_features.keys():
            norm_features[query][para] = fet_val_dict
        else:
            para_val_dict = {para: fet_val_dict}
            norm_features[query] = para_val_dict

    return norm_features


def create_feature_file(rundir: str, qrelsdir: str, qrelfile: str, save: str, name: str, zscore):
    print("Reading runs....")
    runfiles = read_run_files(rundir)
    print("[Done].")

    pool = create_pool(rundir)

    print("Reading qrels...",end=' ')
    qrels = read_ground_truth_file(qrelsdir, qrelfile)
    print("[Done].")

    out_fet_file = save + "/" + name

    feature_dict = create_feature_dict(runfiles, pool)
    if zscore:
        print("Using zscore normalization")
        normalized_feature_dict = convert(normalize_dataframe(dict_to_dataframe(feature_dict)).to_dict("index"))
        fet_line_list = make_feature_file(normalized_feature_dict, qrels)
    else:
        fet_line_list = make_feature_file(feature_dict, qrels)

    print("Writing feature file...",end=' ')
    write_feature_file(fet_line_list, out_fet_file)
    print("[Done].")
    print("Feature file is written to: " + out_fet_file)


def main():
    parser = argparse.ArgumentParser("Create a RankLib compatible feature file.")
    parser.add_argument("--rundir", help="Path to the directory containing the run files", required=True)
    parser.add_argument("--qrelsdir", help="Path to the directory containing the ground truth files", required=True)
    parser.add_argument("--qrelfile", help="Name of the ground truth file file", required=True)
    parser.add_argument("--save", help="Path to the directory where the feature file will be saved", required=True)
    parser.add_argument("--name", help="Name of the feature file", required=True)
    parser.add_argument("--zscore", help="Whether to zscore normalize the features or not. "
                                         "Defaults to no normalization.", action="store_true")
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    create_feature_file(args.rundir, args.qrelsdir, args.qrelfile, args.save, args.name, args.zscore)


if __name__ == '__main__':
    main()