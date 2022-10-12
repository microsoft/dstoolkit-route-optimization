# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from .structure import *
from .logger import *
import collections

class ProblemPartitioner:

    def __init__(self):
        pass

    def partition(self, model_input, max_package_num=30):
        """Function that partitions the big problem into many smaller problems.

        Args:
            model_input: the original model input
            max_package_num: the max number of packages per partition
            
        Returns:
            the list of partitioned model input objects

        """

        # Step 1: partition by package source
        model_input_list_step1 = self.partitionBySrc(model_input)

        # Step 2: further partition if the num of package is larger than threshold
        model_input_list_step2 = []
        for model_input_small in model_input_list_step1:
            if len(model_input_small.all_packages) <= max_package_num:
                model_input_list_step2.append(model_input_small)

            else:
                model_input_list = self.partitionByTimeInterval(model_input_small)
                model_input_list_step2 += model_input_list 

        # Step 3: force to partition by the number of packages
        model_input_list_step3 = []
        for model_input_small in model_input_list_step2:
            if len(model_input_small.all_packages) <= max_package_num:
                model_input_list_step3.append(model_input_small)

            else:
                model_input_list = self.partitionByHardNumber(model_input_small, max_package_num)
                model_input_list_step3 += model_input_list 

        return model_input_list_step3


    def partitionBySrc(self, model_input):
        """Function that partitions the model input by delivery source.
        Constraint: packages from different source cannot be delivered by the same truck.

        Args:
            model_input: the original model input
            
        Returns:
            the list of partitioned model input objects

        """
        model_input_list = []

        same_source_packages = collections.defaultdict(list)

        for p_id, package in model_input.all_packages.items():
            same_source_packages[package.source].append(package)

        for source, packages in same_source_packages.items():
            model_input_small = self.createModelInput(model_input, packages)
            model_input_list.append(model_input_small)

        return model_input_list


    def partitionByTimeInterval(self, model_input):
        """Function that partitions the model input by time interval.
        Constraint: Packages having available time larger than threshold cannot be delivered by the same truck.

        Args:
            model_input: the original model input
            
        Returns:
            the list of partitioned model input objects

        """
        model_input_list = []

        all_packages = list(model_input.all_packages.values())

        candidate_packages = []

        sorted_all_packages = sorted(all_packages, key=lambda p: (p.available_time, p.order_id, p.material_id))

        previous_available_time = 0
        for package in sorted_all_packages:
            if previous_available_time == 0:
                previous_available_time = package.available_time
                candidate_packages.append(package)

            else:
                if abs(package.available_time - previous_available_time) <= model_input.max_time_difference_between_package:
                    previous_available_time = package.available_time
                    candidate_packages.append(package)

                else:
                    model_input_small = self.createModelInput(model_input, candidate_packages)
                    model_input_list.append(model_input_small)

                    candidate_packages = [package]
                    previous_available_time = package.available_time

        # Check if there is any left
        if len(candidate_packages) > 0:
            model_input_small = self.createModelInput(model_input, candidate_packages)
            model_input_list.append(model_input_small)

        return model_input_list
        

    def partitionByHardNumber(self, model_input, max_package_num):
        """Function that partitions the model input by a hard number of packages.

        Args:
            model_input: the original model input
            max_package_num: the max number of packages per partition
            
        Returns:
            the list of partitioned model input objects

        """
        
        model_input_list = []

        all_packages = list(model_input.all_packages.values())

        candidate_packages = []

        sorted_all_packages = sorted(all_packages, key=lambda p: (p.available_time, p.order_id, p.material_id))

        for package in sorted_all_packages:
            if len(candidate_packages) < max_package_num:
                candidate_packages.append(package)
            
            else:
                model_input_small = self.createModelInput(model_input, candidate_packages)
                model_input_list.append(model_input_small)

                candidate_packages = [package]

        # Check if there is any left
        if len(candidate_packages) > 0:
            model_input_small = self.createModelInput(model_input, candidate_packages)
            model_input_list.append(model_input_small)

        return model_input_list
        

    def createModelInput(self, model_input, candidate_packages):
        """Function that create a new model input object.

        Args:
            model_input: the original model input
            candidate_packages: the new list of package
            
        Returns:
            the list of partitioned model input objects

        """
        new_model_input = ModelInput()

        all_packages = {}

        for package in candidate_packages:
            all_packages[package.order_id, package.material_id, package.item_id] = package

        new_model_input.all_packages = all_packages
        new_model_input.distance_matrix = model_input.distance_matrix
        new_model_input.truck_types = model_input.truck_types 
        new_model_input.all_trucks = new_model_input.getAllTrucks(new_model_input.all_packages, new_model_input.truck_types)

        return new_model_input