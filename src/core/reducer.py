# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from .structure import *
from .logger import *
import collections

class SearchSpaceReducer:

    def __init__(self):
        pass

    def reduce1(self, model_input, threshold=0.95):
        """Function to schedule package route by heuristic.
           
           Heuristic: 
           Bigger truck is more cost effecient.
           If packages from a single order can exceed 95% capacity of the biggest truck, 
           then just use one biggest truck to deliver these packages

        Args:
            model_input: the object that stores the model input.
            threshold: the threshold for the truck capacity.

        Returns:
            model_input_reduced: the object for reduced model input
            model_result_partial: the partial scheduling for the identified packaged.

        """

        model_result_partial = ModelResult()
        model_input_reduced = ModelInput()



        same_order_packages = collections.defaultdict(list)

        for key, package in model_input.all_packages.items():
            order_id, material_id, item_id = key

            same_order_packages[order_id].append(package)

        remaining_packages = []

        same_order_packages_sorted = {}

        for order_id, packages in same_order_packages.items():
            source = set()
            destination = set()
            available_time = set()
            danger_type = set()

            for package in packages:
                source.add(package.source)
                destination.add(package.destination)
                available_time.add(package.available_time)
                danger_type.add(package.danger_type)
            # same_order_packages_sorted[order_id] = sorted(packages, key=lambda p: (p.danger_type, p.available_time, p.material_id))

            # Assumption: packages of same order have same source, destination, available_time and danger_type
            assert(len(source) == 1 and len(destination) == 1 and len(available_time) == 1 and len(danger_type) == 1)

        truck_type = model_input.truck_types[0] # truck type is sorted by size

        for order_id, packages in same_order_packages.items():

            candidate_packages = []
            total_area = 0
            total_weight = 0

            for package in packages:
                
                p_id = (package.order_id, package.material_id, package.item_id)

                # Can put into the truck
                if (total_area + package.area <= truck_type.area_capacity and 
                total_weight + package.weight <= truck_type.weight_capacity):
                    candidate_packages.append(package)
                    total_area += package.area
                    total_weight += package.weight

                    # check if the packages are big enough
                    if (total_area > truck_type.area_capacity * threshold or 
                        total_weight > truck_type.weight_capacity * threshold):
                        model_result_partial = self.addResult(candidate_packages, model_result_partial, model_input.distance_matrix, truck_type)

                        candidate_packages = []
                        total_area = 0
                        total_weight = 0

                        continue
                else:
                    candidate_packages = []
                    total_area = 0
                    total_weight = 0

                    continue

        all_packages_reduced = {}
        for key, package in model_input.all_packages.items():
            if key not in model_result_partial.package_assigned_truck:
                all_packages_reduced[key] = package

        # remove the scheduled packages
        model_input_reduced.all_packages = all_packages_reduced
        model_input_reduced.truck_types = model_input.truck_types
        model_input_reduced.distance_matrix = model_input.distance_matrix
        model_input_reduced.all_trucks = model_input.getAllTrucks(model_input_reduced.all_packages, model_input_reduced.truck_types)

        logger.info(f"Number of packages before reduce step: {len(model_input.all_packages)}")
        logger.info(f"Number of packages after reduce step: {len(model_input_reduced.all_packages)}")

        return model_input_reduced, model_result_partial

    def reduce2(self, model_input, threshold=0.95):
        """Function to schedule package route by heuristic.
           
           Heuristic: 
           Bigger truck is more cost effecient.
           If packages to same destination can exceed 95% capacity of the biggest truck, 
           then just use one biggest truck to deliver these packages

        Args:
            model_input: the object that stores the model input.
            threshold: the threshold for the truck capacity.

        Returns:
            model_input_reduced: the object for reduced model input
            model_result_partial: the partial scheduling for the identified packaged.

        """

        model_result_partial = ModelResult()
        model_input_reduced = ModelInput()

        same_destination_packages = collections.defaultdict(list)

        for key, package in model_input.all_packages.items():

            same_destination_packages[package.destination].append(package)

        same_destination_packages_sorted = {}

        # Assumption: packages of same order have same source, destination, available_time and danger_type
        for destination, packages in same_destination_packages.items():
            same_destination_packages_sorted[destination] = sorted(packages, key=lambda p: (p.available_time, p.danger_type, p.order_id))


        truck_type = model_input.truck_types[0] # truck type is sorted by size

        for destination, packages in same_destination_packages_sorted.items():

            candidate_packages = []
            total_area = 0
            total_weight = 0
            danger_types = {}
            min_available_time = float("inf")

            for package in packages:
                
                p_id = (package.order_id, package.material_id, package.item_id)

                # Can put into the truck by capacity constraint
                if (total_area + package.area <= truck_type.area_capacity and 
                total_weight + package.weight <= truck_type.weight_capacity):

                    # Check if they are the same danger type
                    if package.danger_type != 'non_danger':
                        # no other packages, just put this one
                        if len(danger_types) == 0:
                            candidate_packages.append(package)
                            total_area += package.area
                            total_weight += package.weight
                            min_available_time = package.available_time

                        else:
                            # Cannot put this one since it has differnet danger type
                            if package.danger_type not in danger_types:
                                continue
                            # Same danger type with the current packages, can put into the same truch by danger type constraint
                            else:
                                # The gap of the available time is too big, cannot put into the same truck
                                if abs(package.available_time-min_available_time) > model_input.max_time_difference_between_package:
                                    continue
                                
                                # The gap is within the threshold, can put in the same truck by time difference constraint
                                else:
                                    candidate_packages.append(package)
                                    total_area += package.area
                                    total_weight += package.weight
                                    min_available_time = min(min_available_time, package.available_time)

                    # Can put into the truck by danger type constraint
                    else:
                        # The gap of the available time is too big, cannot put into the same truck
                        if abs(package.available_time-min_available_time) > model_input.max_time_difference_between_package:
                            continue
                        
                        # The gap is within the threshold, can put in the same truck by time difference constraint
                        else:
                            candidate_packages.append(package)
                            total_area += package.area
                            total_weight += package.weight
                            min_available_time = min(min_available_time, package.available_time)

                    # check if the packages are big enough
                    if (total_area > truck_type.area_capacity * threshold or 
                        total_weight > truck_type.weight_capacity * threshold):
                        model_result_partial = self.addResult(candidate_packages, model_result_partial, model_input.distance_matrix, truck_type)

                        candidate_packages = []
                        total_area = 0
                        total_weight = 0

                        continue
                else:
                    candidate_packages = []
                    total_area = 0
                    total_weight = 0

                    continue

        all_packages_reduced = {}
        for key, package in model_input.all_packages.items():
            if key not in model_result_partial.package_assigned_truck:
                all_packages_reduced[key] = package

        # remove the scheduled packages
        model_input_reduced.all_packages = all_packages_reduced
        model_input_reduced.truck_types = model_input.truck_types
        model_input_reduced.distance_matrix = model_input.distance_matrix
        model_input_reduced.all_trucks = model_input.getAllTrucks(model_input_reduced.all_packages, model_input_reduced.truck_types)

        logger.info(f"Number of packages before reduce step: {len(model_input.all_packages)}")
        logger.info(f"Number of packages after reduce step: {len(model_input_reduced.all_packages)}")

        return model_input_reduced, model_result_partial

    def addResult(self, candidate_packages, model_result_partial, distance_matrix, truck_type):
        """Function to add new schedule result.
        
        Args:
            candidate_packages: the list of packages to be delivered by the same truck
            model_result_partial: the current partial scheduling.
            distance_matrix: the matrix for storing distance between locations
            truck_speed: the speed of the truck

        Returns:
            model_result_partial: the updated partial scheduling

        """
        # All these packages will put in a single truck with the largest size
        truck = Truck()

        truck.id = uuid.uuid4()
        truck.type = truck_type
        truck_speed = truck_type.speed

        first_package = True

        truck_start_time = max(p.available_time for p in candidate_packages)
        truck_stop_time = truck_start_time + int(distance_matrix.loc[candidate_packages[0].source][candidate_packages[0].destination]/truck_speed)

        model_result_partial.all_trucks[truck.id] = truck

        for p in candidate_packages:
            p_id = (p.order_id, p.material_id, p.item_id)

            model_result_partial.all_packages[p_id] = p

            model_result_partial.package_assigned_truck[p_id] = truck.id

            # Assumption: all package has the same source and destination
            if first_package:
                model_result_partial.truck_assigned_route[truck.id].append(p.source)
                model_result_partial.truck_assigned_route[truck.id].append(p.destination)
                first_package = False

            model_result_partial.truck_assigned_packages[truck.id].append(p_id)
            model_result_partial.package_start_time[p_id] = truck_start_time
            model_result_partial.package_arrival_time[p_id] = truck_stop_time
        
        return model_result_partial


    
