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

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        
        all_packages = ModelInputTest.model_input.getAllPackages(order_file)

        assert(len(all_packages) > 0)

    def test_GetAllPackagesDF(self):

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        order_df = pd.read_csv(order_file)
        
        all_packages = ModelInputTest.model_input.getAllPackages(order_df)

        assert(len(all_packages) > 0)


    def test_getTruckTypes(self):

        truck_types = ModelInputTest.model_input.getTruckTypes()

        assert(len(truck_types) == 4)

    def test_getAllTrucks(self):

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        
        all_packages = ModelInputTest.model_input.getAllPackages(order_file)
        truck_types = ModelInputTest.model_input.getTruckTypes()

        all_trucks = ModelInputTest.model_input.getAllTrucks(all_packages, truck_types)

        assert(len(all_trucks) > 0)

    def test_getDistanceMatrix(self):

        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        distance_matrix = ModelInputTest.model_input.getDistanceMatrix(distance_file)

        assert(distance_matrix.shape[0] > 0)

    def test_getDistanceMatrixDF(self):

        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")
        distance_df = pd.read_csv(distance_file)

        distance_matrix = ModelInputTest.model_input.getDistanceMatrix(distance_df)

        assert(distance_matrix.shape[0] > 0)

    def test_initInputFromFile(self):
        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        ModelInputTest.model_input.initInputFromFile(order_file, distance_file)

        assert(len(ModelInputTest.model_input.all_packages) > 0)
        assert(ModelInputTest.model_input.distance_matrix.shape[0] > 0)


    def test_initInputFromDF(self):
        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        order_df = pd.read_csv(order_file)
        distance_df = pd.read_csv(distance_file)

        ModelInputTest.model_input.initInputFromDF(order_df, distance_df)

        assert(len(ModelInputTest.model_input.all_packages) > 0)
        assert(ModelInputTest.model_input.distance_matrix.shape[0] > 0)

    def test_toScheduleDF(self):

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        ModelInputTest.model_input.initInputFromFile(order_file, distance_file)
        schedule_df = ModelInputTest.model_input.toOrderDF()

        assert(schedule_df.shape[0] > 0)
        assert(schedule_df.shape[0] == len(ModelInputTest.model_input.all_packages))



class ModelResultTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method called to prepare the test fixture.
        """
        
        model_result = ModelResult()

        p_id = ('O1', 'M1', 'P1')
        package = Package()
        package.order_id = p_id[0]
        package.material_id = p_id[1]
        package.plate_id = p_id[2]
        package.danger_type = 'non_danger'
        package.source = 'A'
        package.destination = 'B'
        package.area = 10 * scale_factor
        package.weight = 20000 * scale_factor

        model_result.all_packages[p_id] = package

        type1 = TruckType()
        type1.id = 16.5
        type1.outer_length = 16.5 # in M
        type1.inner_length = 16.1 # in M
        type1.inner_width = 2.5 # in M
        type1.area_capacity = int(type1.inner_length * type1.inner_width * scale_factor)
        type1.weight_capacity = 27000 * scale_factor # in KG  
        type1.speed = 40 / 3.6 # m/s
        type1.cost_per_km = 10 # per KM

        truck = Truck()
        truck.id = 'T1'
        truck.type = type1

        model_result.all_trucks['T1'] = truck
        model_result.package_assigned_truck[p_id] = 'T1'
        model_result.truck_assigned_route['T1'] = ['A', 'B']
        model_result.truck_assigned_packages['T1'] = [p_id]
        model_result.package_start_time[p_id] = 1234567
        model_result.package_arrival_time[p_id] = 2345678

        cls.model_result = model_result

    def test_addResult(self):

        model_result = ModelResult()

        model_result.addResult(ModelResultTest.model_result)

        assert(('O1', 'M1', 'P1') in model_result.all_packages)


    def test_toScheduleDF(self):

        schedule_df = ModelResultTest.model_result.toScheduleDF()

        logger.info(f"Schedule DF: {schedule_df}")

        assert(schedule_df.shape[0] == 1)
