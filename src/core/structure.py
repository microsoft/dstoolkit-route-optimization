# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import pandas as pd
import collections
import uuid
import math
from datetime import datetime

# scale floating value of area and weight to integer with enough precision
scale_factor = 10000

class Package:
    
    # ID
    order_id = None
    material_id = None
    plate_id = None 
    
    # size  
    area = None 
    weight = None
    
    # type of dangerours goods
    danger_type = None
    
    # source and destination
    source = None
    destination = None
    
    # available time and deadline in seconds
    available_time = None
    deadline = None

    # final assignment
    assigned_truck = None
    assigned_stop = None

class TruckType:
    # Type id
    id = None

    # size
    outer_length = None
    
    inner_length = None
    inner_width = None
    
    # area capacity
    area_capacity = None

    # weight capacity
    weight_capacity = None
    
    speed = None
    
    cost_per_kg = None
    
class Truck:
    
    #ID
    id = None
    
    # Type of Truck
    type = None

    assigned_route = None

class ModelInput:

    all_packages = None
    truck_types = None
    all_trucks = None
    max_time_difference_between_package = 2 * 60 * 60 # The available time between two package in the same truck must be less than 2 hours
    stop_time = 6 * 60 * 60 # A truck need to stop for 6 hours in each stop point
    stop_cost = 500 # The cost for each stop
    max_stops = 3 # A truck can stop at most 3 locations

    cost_scale_factor = 1000 # Scale the cost to make it integer

    distance_matrix = None
    _location_list = None
    
    @property
    def location_list(self):
        if self._location_list is None:
            locations = set()

            for key in self.all_packages:
                locations.add(self.all_packages[key].source)
                locations.add(self.all_packages[key].destination)

            locations_list = list(locations)
            locations_list.append("Placeholder") # The last location is reserved as a placeholder. 

            self._location_list = locations_list
            return self._location_list

        else:
            return self._location_list

    def __init__(self):
        pass

    def initInputFromFile(self, order_file, distance_file):
        
        # Initialize the package to be delivered
        self.all_packages = self.getAllPackages(order_file)
        # Initialize the truck types
        self.truck_types = self.getTruckTypes()
        # Initialize the distance matrix
        self.distance_matrix = self.getDistanceMatrix(distance_file)
        # Get the upper bound of trucks we need to use for each truck type
        self.all_trucks = self.getAllTrucks(self.all_packages, self.truck_types)

    def getAllPackages(self, order_file):

        order_df = pd.read_csv(order_file)

        all_packages = {}
        for index, row in order_df.iterrows():
            package = Package()
            package.order_id = row['Order_ID']
            package.material_id = row['Material_ID']
            package.plate_id = row['Plate_ID']
            package.source = row['Source']
            package.destination = row['Destination']
            package.available_time = int(datetime.timestamp(datetime.strptime(row['Available_Time'], '%Y-%m-%d %H:%M:%S')))
            package.deadline = int(datetime.timestamp(datetime.strptime(row['Deadline'], '%Y-%m-%d %H:%M:%S')))
            package.danger_type = row['Danger_Type']
            package.area = row['Area']
            package.weight = row['Weight']

            all_packages[package.order_id, package.material_id, package.plate_id] = package

        return all_packages

    def getTruckTypes(self):
            
        # The cost per KM is scale by 10 to avoid fraction

        type1 = TruckType()
        type1.id = 16.5
        type1.outer_length = 16.5 # in M
        type1.inner_length = 16.1 # in M
        type1.inner_width = 2.5 # in M
        type1.area_capacity = int(type1.inner_length * type1.inner_width * scale_factor)
        type1.weight_capacity = 27000 * scale_factor # in KG  
        type1.speed = 40 / 3.6 # m/s
        type1.cost_per_km = 10 # per KM


        type2 = TruckType()
        type2.id = 12.5
        type2.outer_length = 12.5 # in M
        type2.inner_length = 12.1 # in M
        type2.inner_width = 2.5 # in M
        type2.area_capacity = int(type2.inner_length * type2.inner_width * scale_factor)
        type2.weight_capacity = 24000 * scale_factor # in KG  
        type2.speed = 40/3.6 # m/s
        type2.cost_per_km = 9 # per KM

        type3 = TruckType()
        type3.id = 9.6
        type3.outer_length = 9.6 # in M
        type3.inner_length = 9.1 # in M
        type3.inner_width = 2.3 # in M
        type3.area_capacity = int(type3.inner_length * type3.inner_width * scale_factor)
        type3.weight_capacity = 14000 * scale_factor # in KG  
        type3.speed = 40/3.6 # m/s
        type3.cost_per_km = 6.5 # per KM

        type4 = TruckType()
        type4.id = 7.6
        type4.outer_length = 7.6 # in M
        type4.inner_length = 7.2 # in M
        type4.inner_width = 2.3 # in M
        type4.area_capacity = int(type4.inner_length * type4.inner_width * scale_factor)
        type4.weight_capacity = 8000 * scale_factor # in KG  
        type4.speed = 40/3.6 # m/s
        type4.cost_per_km = 5.5 # per KM

        return [type1, type2, type3, type4]


    def getAllTrucks(self, all_packages, truck_types, sample_data=True, discount_factor=0.6):
        
    #     # Calculate the numebr of trucks we need if no sharing is allowed
    #     for truck_type in truck_types:

        all_trucks = {}
            
        # calculate the minimum number of trucks we need to deliver the package without sharing
        for truck_type in truck_types:
            
            # assumption: the same order id will be delivered to the same destination
            groupby_order_id = collections.defaultdict(list)

            for key, package in all_packages.items():
                groupby_order_id[package.order_id].append(package)

            for order_id, packages in groupby_order_id.items():
                min_num_by_area = math.ceil(sum(package.area for package in packages) / (truck_type.area_capacity))
                min_num_by_capacity = math.ceil(sum(package.weight for package in packages) / truck_type.weight_capacity)

                # Heuristic: bigger truck is more cost efficient, we should use bigger truck more
                if truck_type.id == 12.5 or truck_type.id == 9.6:
                    min_num = int(max(min_num_by_area, min_num_by_capacity) * discount_factor)

                elif truck_type.id == 7.6:
                    min_num = int(max(min_num_by_area, min_num_by_capacity) * discount_factor * discount_factor)
                
                else:
                    min_num = max(min_num_by_area, min_num_by_capacity)

                for i in range(0, min_num):
                    truck = Truck()
                    truck.id = uuid.uuid4()
                    truck.type = truck_type

                    all_trucks[truck.id] = truck
                
        return all_trucks


    def getDistanceMatrix(self, distance_file):
    
        distance_matrix = None

        # distance are in M
        distance_df = pd.read_csv(distance_file)

        distance_matrix_raw = distance_df.pivot('Source', 'Destination', 'Distance(M)')
        assert(distance_matrix_raw.shape[0] == distance_matrix_raw.shape[1])

        distance_matrix = distance_matrix_raw.copy()

        # Add the last one as a placeholder
        distance_matrix["Placeholder"] = 0
        # Add the row for the placeholder location
        distance_matrix.loc["Placeholder"] = [0] * (distance_matrix_raw.shape[1] + 1)
        
        # fill na
        distance_matrix = distance_matrix.fillna(0)
                        
        return distance_matrix

class ModelResult:

    package_assigned_truck = {}
    truck_assigned_route = collections.defaultdict(list)
    truck_assigned_packages = collections.defaultdict(list)
    package_start_time = {}
    package_arrival_time = {}

    def __init__(self):
        pass

    def toScheduleDF(self):
        pass