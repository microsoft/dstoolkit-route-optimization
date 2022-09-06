# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os

parser = argparse.ArgumentParser("reduce")

parser.add_argument("--model_input", type=str, help="the complete list of model input")
parser.add_argument("--distance", type=str, help="the distance file")
parser.add_argument("--model_result_partial", type=str, help="partital result after reduction")
parser.add_argument("--model_input_reduced", type=str, help="the reduced model input")


