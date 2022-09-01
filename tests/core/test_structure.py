import unittest
import os

from src.core.structure import *

work_dir = os.path.dirname(os.path.abspath(__file__))

class ModelInputTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method called to prepare the test fixture.
        """
        
        cls.model_input = ModelInput()

    def test_GetAllPackages(self):

        order_file = os.path.join(work_dir, "../../sample_data/order.csv")
        
        all_packages = ModelInputTest.model_input.getAllPackages(order_file)

        assert(len(all_packages) > 0)


    def test_getTruckTypes(self):

        truck_types = ModelInputTest.model_input.getTruckTypes()

        assert(len(truck_types) == 4)

    def test_getAllTrucks(self):

        order_file = os.path.join(work_dir, "../../sample_data/order.csv")
        
        all_packages = ModelInputTest.model_input.getAllPackages(order_file)
        truck_types = ModelInputTest.model_input.getTruckTypes()

        all_trucks = ModelInputTest.model_input.getAllTrucks(all_packages, truck_types)

        assert(len(all_trucks) > 0)

    def test_getDistanceMatrix(self):

        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        distance_matrix = ModelInputTest.model_input.getDistanceMatrix(distance_file)

        assert(distance_matrix.shape[0] > 0)

