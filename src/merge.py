# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os

parser = argparse.ArgumentParser("merge")

parser.add_argument("--model_input", type=str, help="the complete model input")
parser.add_argument("--model_result_partial", type=str, help="the partial result during the reduce step")
parser.add_argument("--model_result_list", type=str, help="the list of itermediate model results")
parser.add_argument("--model_result_final", type=str, help="final model result directory")

args = parser.parse_args()
merger = None
