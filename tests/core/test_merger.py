import unittest
import os

from src.core.merger import *

work_dir = os.path.dirname(os.path.abspath(__file__))

class MergerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Method called to prepare the test fixture.
        """
        
        cls.merger = ResultMerger()

        order_file = os.path.join(work_dir, "../../sample_data/order_large.csv")
        distance_file = os.path.join(work_dir, "../../sample_data/distance.csv")

        model_input = ModelInput()
        model_input.initInputFromFile(order_file, distance_file)

        cls.model_input = model_input

    def test_merge(self):
        
        type1 = TruckType()
        type1.id = 16.5
        type1.outer_length = 16.5 # in M
        type1.inner_length = 16.1 # in M
        type1.inner_width = 2.5 # in M
        type1.area_capacity = int(type1.inner_length * type1.inner_width * scale_factor)
        type1.weight_capacity = 27000 * scale_factor # in KG  
        type1.speed = 40 / 3.6 # m/s
        type1.cost_per_km = 10 # per KM

        # Result 1
        model_result1 = ModelResult()
        p_id_1 = ('O1', 'M1', 'P1')
        package1 = Package()
        package1.order_id = p_id_1[0]
        package1.material_id = p_id_1[1]
        package1.item_id = p_id_1[2]
        package1.danger_type = 'non_danger'
        package1.source = 'A'
        package1.destination = 'B'
        package1.area = 10 * scale_factor
        package1.weight = 20000 * scale_factor

        model_result1.all_packages[p_id_1] = package1
        truck1 = Truck()
        truck1.id = 'T1'
        truck1.type = type1

        model_result1.all_trucks['T1'] = truck1
        model_result1.package_assigned_truck[p_id_1] = 'T1'
        model_result1.truck_assigned_route['T1'] = ['A', 'B']
        model_result1.truck_assigned_packages['T1'] = [p_id_1]
        model_result1.package_start_time[p_id_1] = 1234567
        model_result1.package_arrival_time[p_id_1] = 2345678

        # Result 2
        model_result2 = ModelResult()
        p_id_2 = ('O2', 'M1', 'P1')
        package2 = Package()
        package2.order_id = p_id_2[0]
        package2.material_id = p_id_2[1]
        package2.item_id = p_id_2[2]
        package2.danger_type = 'type_1'
        package2.source = 'A'
        package2.destination = 'B'
        package2.area = 10 * scale_factor
        package2.weight = 20000 * scale_factor

        model_result2.all_packages[p_id_2] = package2
        truck2 = Truck()
        truck2.id = 'T2'
        truck2.type = type1

        model_result2.all_trucks['T2'] = truck2
        model_result2.package_assigned_truck[p_id_2] = 'T2'
        model_result2.truck_assigned_route['T2'] = ['A', 'B']
        model_result2.truck_assigned_packages['T2'] = [p_id_2]
        model_result2.package_start_time[p_id_2] = 87654321
        model_result2.package_arrival_time[p_id_2] = 98765432

        model_result_final = MergerTest.merger.merge(MergerTest.model_input, [model_result1.toScheduleDF(), model_result2.toScheduleDF()])

        logger.info(f"Final schedule DF: {model_result_final}")

        assert(model_result_final.shape[0] == 2)


