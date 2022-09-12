import argparse
import os
from core.structure import *
from core.model import *

def init():
    global args_distance
    parser = argparse.ArgumentParser("solve")
#    parser.add_argument("--model_input_list", type=str, help="the complete list of model input")
    parser.add_argument("--distance", type=str, help="the distance file")

    args = parser.parse_args()
#    print("Argument 1: %s" % args.model_input_list)
    print("Argument 2: %s" % args.distance)

    args_distance = args.distance


def run(mini_batch):
    print(f'ParallelRun start: {mini_batch}')
    model_input_partion = ModelInput()
    model_input_partion.initInputFromFile(mini_batch, args_distance)

    model = Model()
    model.setModelInput(model_input_partion)

    model.createVariables()
    model.setConstraints()
    model.setObjective(objective="Cost")
    model.solve()
    print(model.getModelResult())
    return model.getModelResult()
    
#    model_result_file = os.path.join(tmp_folder, f"model_result_partition_{i}.csv")
#    model_result.toScheduleDF().to_csv(model_result_file, index=False)

