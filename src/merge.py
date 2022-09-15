# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os

from core.structure import *
from core.merger import *

parser = argparse.ArgumentParser("merge")

parser.add_argument("--model_input", type=str, help="the complete model input")
parser.add_argument("--distance", type=str, help="the distance file")
parser.add_argument("--model_result_partial", type=str, help="the partial result during the reduce step")
parser.add_argument("--model_result_list", type=str, help="the list of itermediate model results")
parser.add_argument("--model_result_final", type=str, help="final model result directory")

args = parser.parse_args()

# Create result merger
merger = ResultMerger()

partial_result_df = pd.read_csv(args.model_result_partial + "/model_result_partial.csv")
result_list = pd.read_csv(args.model_result_list + '/model_result_list.txt', header=None, delimiter=' ')
result_list.columns = partial_result_df.columns

results = [partial_result_df, result_list]

model_input_origin = ModelInput()
model_input_origin.initInputFromFile(args.model_input, args.distance)
model_final_result = merger.merge(model_input_origin, results)

## Save the results
model_final_result.to_csv(args.model_result_final + "/schedule.csv", index=False)
