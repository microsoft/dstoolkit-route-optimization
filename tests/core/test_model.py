import unittest
import os

from src.core.model import *

work_dir = os.path.dirname(os.path.abspath(__file__))

class ModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method called to prepare the test fixture.
        """
        
        cls.model = Model()

        order_file = os.path.join(work_dir, "../../sample_data/order_small.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        model_input = ModelInput()
        model_input.initInputFromFile(order_file, distance_file)

        cls.model.model_input = model_input

    def test_00_solve(self):

        # Create necessary variables
        ModelTest.model.createVariables()

        # Set all constraints
        ModelTest.model.setConstraints()

        # Set the objective function
        ModelTest.model.setObjective(objective="Cost")

        # Solve the problem
        ModelTest.model.solve()

        # Get objective value
        objective_value = ModelTest.model.getObjectiveValue()

    def test_01_getModelResult(self):

        model_result = ModelTest.model.getModelResult()

        assert(len(model_result.truck_assigned_packages) > 0)

