# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os
import glob

from azureml.core import Workspace, Dataset, Experiment, Run

from core.reducer import *
from core.structure import *

parser = argparse.ArgumentParser("reduce")

parser.add_argument("--model_input", type=str, help="the complete list of model input")
parser.add_argument("--distance", type=str, help="the distance file")
parser.add_argument("--model_result_partial", type=str, help="partital result after reduction")
parser.add_argument("--model_input_reduced", type=str, help="the reduced model input")


args = parser.parse_args()

print("Argument 1: %s" % args.model_input)
print("Argument 2: %s" % args.distance)
print("Argument 3: %s" % args.model_result_partial)
print("Argument 4: %s" % args.model_input_reduced)

# Get the experiment run context
# run = Run.get_context()
# model_input = run.input_datasets['model_input'] 
# distance = run.input_datasets['distance'] 

# model_input_file = glob.glob(model_input + "/*.csv")[0]
# distance_file =  glob.glob(distance + "/*.csv")[0]

## Instanciation
reducer = SearchSpaceReducer()
model_input_origin = ModelInput()
model_input_origin.initInputFromFile(args.model_input, args.distance)

## Reduce process
model_input_reduced, model_result_partial = reducer.reduce1(model_input_origin)
#model_input_reduced, model_result_partial = reducer.reduce2(model_input_origin)

## Save the results

os.makedirs(args.model_result_partial)
os.makedirs(args.model_input_reduced)

model_input_reduced.toOrderDF().to_csv(args.model_input_reduced + "/order_reduced.csv", index=False)
model_result_partial.toScheduleDF().to_csv(args.model_result_partial + "/model_result_partial.csv", index=False)