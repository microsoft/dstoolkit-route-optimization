import unittest
import os

from src.core.partitioner import *

work_dir = os.path.dirname(os.path.abspath(__file__))

class PartitionerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method called to prepare the test fixture.
        """
        
        cls.partitioner = ProblemPartitioner()

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        model_input = ModelInput()
        model_input.initInputFromFile(order_file, distance_file)

        cls.model_input = model_input

    def test_partition(self):

        max_package_num = 20

        model_input_list = PartitionerTest.partitioner.partition(PartitionerTest.model_input, max_package_num)

        number_packages = 0
        for model_input in model_input_list:
            assert(len(model_input.all_packages) <= max_package_num)
            number_packages += len(model_input.all_packages)

        logger.info(f"Number of packages before partitioned: {len(PartitionerTest.model_input.all_packages)}, after partition: {number_packages}")

        assert(number_packages == len(PartitionerTest.model_input.all_packages))

    def test_partitionByHardNumber(self):

        model_input_list = PartitionerTest.partitioner.partitionByHardNumber(PartitionerTest.model_input, 30)

        number_packages = 0
        for model_input in model_input_list:
            number_packages += len(model_input.all_packages)      

        assert(number_packages == len(PartitionerTest.model_input.all_packages))


