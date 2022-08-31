# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import pandas as pd
import collections
import uuid
import math
from datetime import datetime
from .logger import *

# scale floating value of area and weight to integer with enough precision
scale_factor = 10000

class Package:
    
    def __init__(self):
        # ID
        self.order_id = None
        self.material_id = None
        self.plate_id = None 
        
        # size  
        self.area = None 
        self.weight = None
        
        # type of dangerours goods
        self.danger_type = None
        
        # source and destination
        self.source = None
        self.destination = None
        
        # available time and deadline in seconds
        self.available_time = 0
        self.deadline = 0


class TruckType:
    
    def __init__(self):
        # Type id
        self.id = None

        # size
        self.outer_length = None
        
        self.inner_length = None
        self.inner_width = None
        
        # area capacity
        self.area_capacity = None

        # weight capacity
        self.weight_capacity = None
        
        self.speed = None
        
        self.cost_per_kg = None
    
class Truck:
    
    def __init__(self):
        #ID
        self.id = None
        
        # Type of Truck
        self.type = None


class ModelInput:
    
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
        self.all_packages = None
        self.truck_types = None
        self.all_trucks = None
        self.max_time_difference_between_package = 2 * 60 * 60 # The available time between two package in the same truck must be less than 2 hours
        self.stop_time = 6 * 60 * 60 # A truck need to stop for 6 hours in each stop point
        self.stop_cost = 500 # The cost for each stop
        self.max_stops = 3 # A truck can stop at most 3 locations

        self.cost_scale_factor = 1000 # Scale the cost to make it integer

        self.distance_matrix = None
        self._location_list = None

    def initInputFromFile(self, order_file, distance_file):
        """Function that initialize model input from files.

        Args:
            order_file: the file that stores the order
            distance_file: the file that stores the pair-wised distance
            
        Returns:
            None

        """
        
        # Initialize the package to be delivered
        self.all_packages = self.getAllPackages(order_file)
        # Initialize the truck types
        self.truck_types = self.getTruckTypes()
        # Initialize the distance matrix
        self.distance_matrix = self.getDistanceMatrix(distance_file)
        # Get the upper bound of trucks we need to use for each truck type
        self.all_trucks = self.getAllTrucks(self.all_packages, self.truck_types)

    def getAllPackages(self, order_file):
        """Function that constructs the list of packages from a file.

        Args:
            order_file: the file that stores the order
            
        Returns:
            A list of package objects.

        """
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
        """Function that create the list of truck type we can use.

        Args:
            None
            
        Returns:
            A list of truck types.

        """
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


    def getAllTrucks(self, all_packages, truck_types, discount_factor=0.6):
        """Function that calculate the number of trucks for each type we need.

        Args:
            all_packages: the list of packages to be delivered.
            truck_types: the list of truck types
            discount_factor: discount_factor to the smaller truck.
            
        Returns:
            A list of truck objects.

        """
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
        """Function that constructs the distance matrix from a file.

        Args:
            distance_file: a file that stores the pair-wise distance.
            
        Returns:
            A DataFrame object that stores the pair-wise distance.

        """
    
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

    def toOrderDF(self):
        """Function that convert the model input into DataFrame format.

        Args:
            None
            
        Returns:
            A DataFrame that stores the orders.

        """
        order_list = []

        columns = [
            "Order_ID",
            "Material_ID",
            "Plate_ID",
            "Source",
            "Destination",
            "Available_Time",
            "Deadline",
            "Danger_Type",
            "Area",
            "Weight"
        ]

        for p_id, p in self.all_packages.items():
            order = (p.order_id, 
                     p.material_id, 
                     p.plate_id, 
                     p.source,
                     p.destination,
                     datetime.fromtimestamp(p.available_time),
                     datetime.fromtimestamp(p.deadline),
                     p.danger_type,
                     p.area,
                     p.weight,
                    )
            
            order_list.append(order)

        order_df = pd.DataFrame(order_list, columns=columns).sort_values(['Order_ID', 'Material_ID'])

        return order_df

class ModelResult:

    def __init__(self):
        self.all_packages = {}
        self.all_trucks = {}

        self.package_assigned_truck = {}
        self.truck_assigned_route = collections.defaultdict(list)
        self.truck_assigned_packages = collections.defaultdict(list)
        self.package_start_time = {}
        self.package_arrival_time = {}

    def addResult(self, partial_result):
        """Function that adds partial result to the current one.

        Args:
            partial_result: the partial model result
            
        Returns:
            None

        """

        # works in python 3.5 or higher
        self.all_packages = {**self.all_packages, **partial_result.all_packages}
        self.all_trucks = {**self.all_trucks, **partial_result.all_trucks}

        self.package_assigned_truck = {**self.package_assigned_truck, **partial_result.package_assigned_truck}
        self.truck_assigned_route = {**self.truck_assigned_route, **partial_result.truck_assigned_route}
        self.truck_assigned_packages = {**self.truck_assigned_packages, **partial_result.truck_assigned_packages}
        self.package_start_time = {**self.package_start_time, **partial_result.package_start_time}
        self.package_arrival_time = {**self.package_arrival_time, **partial_result.package_arrival_time}
               

    def toScheduleDF(self):
        """Function that convert the model result into DataFrame format.

        Args:
            None
            
        Returns:
            A DataFrame that stores the route schedualing.

        """

        columns = [
            "Schedule_ID",
            "Truck_Route",
            "Order_ID",
            "Material_ID",
            "Plate_ID",
            "Danger_Type",
            "Source",
            "Destination",
            "Start_Time",
            "Arrival_Time",
            "Deadline",
            "Shared_Truck",
            "Truck_Type",
            "Area_Rate",
            "Weight_Rate",
            "Capacity_Rate"
        ]
        
        schedule_list = []
        
        truck_assigned_order = {}
        truck_area_rate = {}
        truck_weight_rate = {}
        truck_capacity_rate = {}

        for t_id, packages in self.truck_assigned_packages.items():
            truck_assigned_order[t_id] = set([self.all_packages[p].order_id for p in packages])
            truck_area_rate[t_id] = sum([self.all_packages[p].area for p in packages])/self.all_trucks[t_id].type.area_capacity
            truck_weight_rate[t_id] = sum([self.all_packages[p].weight for p in packages])/self.all_trucks[t_id].type.weight_capacity
            truck_capacity_rate[t_id] = max(truck_area_rate[t_id], truck_weight_rate[t_id])
        
        for t_id, packages in self.truck_assigned_packages.items():
            for p_id in packages:
                p = self.all_packages[p_id]

                schedule = (t_id, 
                            "->".join(self.truck_assigned_route[t_id]), 
                            p.order_id, 
                            p.material_id, 
                            p.plate_id, 
                            p.danger_type,
                            p.source,
                            p.destination,
                            datetime.fromtimestamp(self.package_start_time[p_id]), 
                            datetime.fromtimestamp(self.package_arrival_time[p_id]),
                            datetime.fromtimestamp(p.deadline),
                            "Y" if len(truck_assigned_order[t_id]) > 1 else "N",
                            self.all_trucks[t_id].type.id,
                            truck_area_rate[t_id],
                            truck_weight_rate[t_id],
                            truck_capacity_rate[t_id]
                        )

                schedule_list.append(schedule)

        schedule_df = pd.DataFrame(schedule_list, columns=columns).sort_values(['Schedule_ID', 'Order_ID', 'Material_ID'])

        return schedule_df