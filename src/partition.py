# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import os

parser = argparse.ArgumentParser("partition")

parser.add_argument("--model_input_reduced", type=str, help="the reduced model input")
parser.add_argument("--model_input_list", type=str, help="the list of partitioned model input")