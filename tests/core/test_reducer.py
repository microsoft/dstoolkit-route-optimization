import unittest
import os

from src.core.reducer import *

work_dir = os.path.dirname(os.path.abspath(__file__))

class ReducerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method called to prepare the test fixture.
        """
        
        cls.reducer = SearchSpaceReducer()

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        model_input = ModelInput()
        model_input.initInputFromFile(order_file, distance_file)

        cls.model_input = model_input

    def test_reduce1(self):
        logger.info("Testing reduce heuristic 1")
        model_input_reduced, model_result_partial = ReducerTest.reducer.reduce1(ReducerTest.model_input)

        model_input_reduced.toOrderDF()
        model_result_partial.toScheduleDF()


    def test_reduce2(self):
        logger.info("Testing reduce heuristic 2")
        model_input_reduced, model_result_partial = ReducerTest.reducer.reduce2(ReducerTest.model_input)

        model_input_reduced.toOrderDF()
        model_result_partial.toScheduleDF()


