# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os

from core.structure import *
from core.partitioner import *

parser = argparse.ArgumentParser("partition")

parser.add_argument("--model_input_reduced", type=str, help="the reduced model input")
parser.add_argument("--distance", type=str, help="the distance file")
parser.add_argument("--model_input_list", type=str, help="the list of partitioned model input")

args = parser.parse_args()
print("Argument 1: %s" % args.model_input_reduced)
print("Argument 2: %s" % args.distance)
print("Argument 3: %s" % args.model_input_list)

## Instanciation
partitioner = ProblemPartitioner()
model_input_reduced = ModelInput()
model_input_reduced.initInputFromFile(args.model_input_reduced + "/order_reduced.csv", args.distance)

## Partition process
max_package_num = 30
model_input_list = partitioner.partition(model_input_reduced, max_package_num)

os.mkdir(args.model_input_list)
## Save the results
i = 0
for model_input_partition in model_input_list:
    model_input_partition_file = os.path.join(args.model_input_list, f"order_partition_{i}.csv")
    print(f"{args.model_input_list} created.")
    print(model_input_partition_file)
    model_input_partition.toOrderDF().to_csv(model_input_partition_file, index=False)
    i += 1