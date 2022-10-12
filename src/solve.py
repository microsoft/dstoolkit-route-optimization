# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os
import pandas as pd

from core.structure import *
from core.model import *

parser = argparse.ArgumentParser("solve")
parser.add_argument('--distance', type=str, help="the distance file")

args, _ = parser.parse_known_args()
distance_file = args.distance

print(f'Distance file: {distance_file}')

def init():
    pass 

def run(input_data):
    print(f'ParallelRun input data: {input_data}')

    results = []
    # Solve each smaller problem
    for order_file in input_data:
        model_input_partion = ModelInput()
        model_input_partion.initInputFromFile(order_file, distance_file)

        model = Model()
        model.setModelInput(model_input_partion)

        model.createVariables()
        model.setConstraints()
        model.setObjective(objective="Cost")
        model.solve()
        print(model.getModelResult().toScheduleDF())

        results.append(model.getModelResult().toScheduleDF())
    
    return pd.concat(results)
