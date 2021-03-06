from __future__ import print_function

import itertools
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import column_or_1d
import numpy as np

from data.D32 import D32Parser
from data.D36 import D36Parser
from data.TMG15 import TMG15Parser
from data.TS16 import TS16Parser
from data.D32M4 import D32M4Parser
from models.expirament_utils import create_pipelines, run_cv_and_test, get_hypertune_params, \
    run_cv_and_test_hypertuned_params

# Global_vars
seed = 1234
num_folds = 10
n_jobs = -1
hypertuned_experiment = True


if __name__ == '__main__':

    parsers = [D32Parser, D36Parser, TMG15Parser, TS16Parser, D32M4Parser]

    for parser_class in parsers:

        # Read datasets
        parser = parser_class()
        scoring = parser.metric
        print("Working on " + parser.name + " dataset")
        print("Metric: " + parser.metric)

        X, y = parser.X, parser.y


        y_sonar = column_or_1d(y, warn=False)
        X_train, X_test, y_train, y_test = train_test_split(X, y_sonar, test_size=0.20, random_state=seed)

        # Create pipelines
        pipelines = create_pipelines(seed)

        # Run cv experiment without hyper_param_tuning
        results_df = run_cv_and_test(X_train, y_train, X_test, y_test, pipelines, scoring, seed, num_folds,
                                     dataset_name=parser.name, n_jobs=n_jobs)

        # Save cv experiment to csv
        dataset_results_name = parser.name + "_results.csv"
        results_path = os.path.join("..", "..", "data", "processed", dataset_results_name)
        results_df.to_csv(results_path, index=False)


        if hypertuned_experiment:
            # Run same experiment with hypertuned parameters
            print("#"*30 + "Hyper tuning parameters" "#"*30)
            hypertuned_params = get_hypertune_params()

            hypertune_results_df = run_cv_and_test_hypertuned_params(X_train, y_train, X_test, y_test, pipelines, scoring, seed,
                                                                     num_folds, dataset_name=parser.name, n_jobs=n_jobs,
                                                                     hypertuned_params=hypertuned_params,)
            dataset_results_name = parser.name + "_results_hypertuned.csv"
            results_path = os.path.join("..", "..", "data", "processed", dataset_results_name)
            hypertune_results_df.to_csv(results_path, index=False)
