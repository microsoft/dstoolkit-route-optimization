import unittest
import os
import shutil
import glob

from src.core.reducer import *
from src.core.partitioner import *
from src.core.model import *
from src.core.merger import *

work_dir = os.path.dirname(os.path.abspath(__file__))

class PipelineTest(unittest.TestCase):

    def test_pipeline(self):

        order_file = os.path.join(work_dir, "../../sample_data/order_small.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        tmp_folder = os.path.join(work_dir, "../../tmp")

        if not os.path.exists(tmp_folder):
            os.makedirs(tmp_folder)

        else:
            shutil.rmtree(tmp_folder)
            os.makedirs(tmp_folder)

        model_input_origin = ModelInput()
        model_input_origin.initInputFromFile(order_file, distance_file)


        # Step 1 - Reduce the search space:
        # Initialize reducer
        reducer = SearchSpaceReducer()

        # Get the reduced model input and partial model result
        model_input_reduced, model_result_partial = reducer.reduce2(model_input_origin)

        # write the reduced model input to file
        model_input_reduced_file = os.path.join(tmp_folder, "order_reduced.csv")
        model_input_reduced.toOrderDF().to_csv(model_input_reduced_file, index=False)

        # write the partial model result to file
        model_result_partial_file = os.path.join(tmp_folder, "model_result_partial.csv")
        model_result_partial.toScheduleDF().to_csv(model_result_partial_file, index=False)        

        # Step 2 - Partition the problem into smaller problems
        # Initialize partitioner
        partitioner = ProblemPartitioner()

        model_input_reduced = ModelInput()
        model_input_reduced.initInputFromFile(model_input_reduced_file, distance_file)

        max_package_num = 30
        model_input_list = partitioner.partition(model_input_reduced, max_package_num)
        logger.info(f"Number of partitions: {len(model_input_list)}")

        # Write to files
        i = 0
        for model_input_partition in model_input_list:
            model_input_partition_file = os.path.join(tmp_folder, f"model_input_partition_{i}.csv")
            model_input_partition.toOrderDF().to_csv(model_input_partition_file, index=False)
            i += 1

        # Step 3 - Solve each smaller problems
        model_input_partition_file_list = glob.glob(os.path.join(tmp_folder,'model_input_partition_*.csv'))
        
        i = 0
        for partition_file in model_input_partition_file_list:
            model_input_partion = ModelInput()
            model_input_partion.initInputFromFile(partition_file, distance_file)

            model = Model()
            model.setModelInput(model_input_partion)

            model.createVariables()
            model.setConstraints()
            model.setObjective(objective="Cost")
            model.solve()

            model_result = model.getModelResult()
            
            model_result_file = os.path.join(tmp_folder, f"model_result_partition_{i}.csv")
            model_result.toScheduleDF().to_csv(model_result_file, index=False)
            i += 1

        # Step 4: Merge the individual results
        # Initialize result merger
        merger = ResultMerger()

        model_result_list = []

        model_result_partial_df = pd.read_csv(model_result_partial_file)
        model_result_list.append(model_result_partial_df)

        model_result_partition_file_list = glob.glob(os.path.join(tmp_folder,'model_result_partition_*.csv'))
        for partition_file in model_result_partition_file_list:
            model_result_list.append(pd.read_csv(partition_file))

        model_final_result = merger.merge(model_input_origin, model_result_list)

        logger.info(f"Final model result: {model_final_result}")

        assert(len(model_input_origin.all_packages) == model_final_result.shape[0])


        

        

        



