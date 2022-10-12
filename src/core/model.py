# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

from ortools.sat.python import cp_model
import collections

from .structure import *
from .logger import * 

work_dir = os.path.dirname(os.path.abspath(__file__))

class Model:

    model = None
    solver = None
    model_input = None
    model_result = None

    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

    def setObjective(self, objective):
        """Function that sets the objective of the model.

        Args:
            objective: The tyoe of objective.
            
        Returns:
            None

        """

        if objective == 'Cost':
            self.setCostObjective()

        else:
            logger.info("No valid objective is set. The valid objectives are: Cost")
            sys.exit(1)

    def setConstraints(self):
        """Function that sets the constraints of the model.

        Args:
            None
            
        Returns:
            None

        """
        self.setDangerTypeConstraint()
        self.setFixedSrcConstraint()
        self.setPackageTimeWindowConstraint()
        self.setPackageTruckAssignmentConstraint()
        self.setPackageArrivalTimeConstraint()
        self.setPackageStartTimeConstraint()
        self.setTruckVolumeCapacityConstraint()
        self.setTruckWeightCapacityConstraint()

    def setHints(self, *args):
        """Function that sets the search hints of the model.

        Args:
            None
            
        Returns:
            None

        """
        pass

    def solve(self, max_time_in_seconds=120):
        """Function that solves the optimization problem.

        Args:
            max_time_in_seconds: the maximum search time of the solver.
            
        Returns:
            None

        """
        import multiprocessing

        class SolutionPrinter(cp_model.CpSolverSolutionCallback):

            def __init__(self):
                cp_model.CpSolverSolutionCallback.__init__(self)
                self.__solution_count = 0

            def on_solution_callback(self):
                self.__solution_count += 1

            def solution_count(self):
                return self.__solution_count

        # self.solver.parameters.num_search_workers = max(1, multiprocessing.cpu_count()-1)
        self.solver.parameters.num_search_workers = 1
        self.solver.parameters.max_time_in_seconds = max_time_in_seconds # Solver will stop after this number of seconds

        printer = SolutionPrinter()
        status = self.solver.SolveWithSolutionCallback(self.model, printer)

        # Limit the number of search
        # status = self.solver.SearchForAllSolutions(self.model, logger.infoer)

        if status == cp_model.OPTIMAL:
            logger.info("Optimal solution is found.")

        elif status == cp_model.FEASIBLE:
            logger.info("A feasible solution was found, but we don't know if it's optimal.")

        elif status == cp_model.INFEASIBLE:
            logger.info("The problem was proven infeasible.")                
            self.validateInput()
            
            logger.info(f"Number of conflicts: {self.solver.NumConflicts()}")

        elif status == cp_model.MODEL_INVALID:
            logger.info("The given model didn't pass the validation step.")
            logger.info(self.model.Validate())
            self.validateInput()
            
            logger.info(f"Number of conflicts: {self.solver.NumConflicts()}")

        elif status == cp_model.UNKNOWN:
            logger.info("The status of the model is unknown because a search limit was reached.")

    def setModelInput(self, model_input):
        """Function that sets the model input object.

        Args:
            model_input: the object that stores the model input.
            
        Returns:
            None

        """
        self.model_input = model_input

    def getModelResult(self):
        """Function that gets the final route schedule after problem is solved.

        Args:
            None
            
        Returns:
            model_result: the result of the model

        """

        package_assigned_truck = {}
    
        for key in self.truck_to_packages:
            
            if self.solver.Value(self.truck_to_packages[key]) == 1:
                t_id, p_id = key
                package_assigned_truck[p_id] = t_id

        truck_assigned_packages = collections.defaultdict(list)
        
        for p_id, t_id in package_assigned_truck.items():
            truck_assigned_packages[t_id].append(p_id)

        
        truck_assigned_route = collections.defaultdict(list)
        for t_id in truck_assigned_packages:
            stops = {}

            first_package = True

            for p_id in truck_assigned_packages[t_id]:
                
                # Assumption: All packages have the same source
                source = self.model_input.all_packages[p_id].source
                package_stop = self.solver.Value(self.package_stops[p_id])
                if package_stop in stops:
                    assert(self.model_input.all_packages[p_id].destination == stops[package_stop])
                else:
                    stops[package_stop] = self.model_input.all_packages[p_id].destination

            route = [(stop, destination) for stop, destination in stops.items()] 

            route = sorted(route, key=lambda x: x[0])
            
            truck_assigned_route[t_id] = [source] + [destination for stop, destination in route]

        package_start_time = {}

        for key in self.package_start_time:
            package_start_time[key] = self.solver.Value(self.package_start_time[key])

        package_arrival_time = {}

        for key in self.package_arrival_time:
            package_arrival_time[key] = self.solver.Value(self.package_arrival_time[key])
      
        self.model_result = ModelResult()
        self.model_result.all_packages = self.model_input.all_packages
        self.model_result.all_trucks = self.model_input.all_trucks
        self.model_result.package_assigned_truck = package_assigned_truck
        self.model_result.truck_assigned_route = truck_assigned_route
        self.model_result.truck_assigned_packages = truck_assigned_packages
        self.model_result.package_start_time = package_start_time
        self.model_result.package_arrival_time = package_arrival_time

        return self.model_result

    def getObjectiveValue(self):
        """Function that gets objective value after problem is solved.

        Args:
            None
            
        Returns:
            the objevtive value.

        """
        return self.solver.ObjectiveValue()

    def createVariables(self):
        """Function that creates necessary global decision variables.

        Args:
            None
            
        Returns:
            None

        """

        logger.info("Creating variables")

        def get_min_max_start_time(all_packages):
            
            min_start = float('inf')
            max_start = 0
            
            for key in all_packages:
                package = all_packages[key]
                if package.available_time > max_start:
                    max_start = package.available_time
                if package.available_time < min_start:
                    min_start = package.available_time
                            
            return int(min_start), int(max_start)

        def get_max_deadline(all_packages):
            
            max_deadline = 0
            
            for key in all_packages:
                package = all_packages[key]
                if package.deadline > max_deadline:
                    max_deadline = package.deadline
                    
            return max_deadline

        self.min_start, self.max_start = get_min_max_start_time(self.model_input.all_packages)
        self.max_deadline = get_max_deadline(self.model_input.all_packages)


        # The truck to package assignment variables
        truck_to_packages = {}
        package_stops = {}

        all_orders = set()

        for p_id in self.model_input.all_packages:
            package = self.model_input.all_packages[p_id]

            package_stop_var = self.model.NewIntVar(1, self.model_input.max_stops, f'package_stops[{p_id}]')

            package_stops[p_id] = package_stop_var

            for t_id in self.model_input.all_trucks:
                assignment_var = self.model.NewBoolVar(f'truck_to_package_assignment[{t_id}, {p_id}]')
                
                truck_to_packages[t_id, p_id] = assignment_var 
                
                all_orders.add(package.order_id)
        
        same_truck_packages = {}
        for p_id_1 in self.model_input.all_packages:
  
            for p_id_2 in self.model_input.all_packages:

                if p_id_1 != p_id_2:
                    if (p_id_1, p_id_2) in same_truck_packages or (p_id_2, p_id_1) in same_truck_packages:
                        continue
                    else:
                        assignment_var = self.model.NewBoolVar(f'same_truck_packages[{p_id_1}, {p_id_2}]')
                
                        same_truck_packages[p_id_1, p_id_2] = assignment_var 


        self.package_start_time = {}

        for p_id in self.model_input.all_packages:
            start_time_var = self.model.NewIntVar(self.min_start, self.max_start, f'start_time_[{p_id}]')
            self.package_start_time[p_id] = start_time_var

        self.truck_to_packages = truck_to_packages
        self.package_stops = package_stops

        self.same_truck_packages = same_truck_packages
    
        self.countVariables()

    def countVariables(self):
        """Function that counts how many decision variables and constraints being created.

        Args:
            None
            
        Returns:
            None

        """
        logger.info(f"Number of Variables:{str(vars(self.model)).count('variables')}; Number of Constraints: {str(vars(self.model)).count('constraints')}")

    def validateInput(self):
        """Function that validates if there are any violation of the constraints before modeling.

        Args:
            None
            
        Returns:
            None

        """
        # Check if there is any constraint violation before modeling
            
        # Check if the truck is fast enough to get to the destination
        truck_being_used = set()
        for p_id in self.model_input.all_packages:
            package = self.model_input.all_packages[p_id]
            
            allocated = False
            
            for t_id in self.model_input.all_trucks: 
                if t_id not in truck_being_used:
                    truck = self.model_input.all_trucks[t_id]
                    
                    if self.model_input.distance_matrix.loc[package.source][package.destination] / truck.type.speed <= (package.deadline - package.available_time):
                        truck_being_used.add(t_id)
                        allocated = True
                        break
                    
            if not allocated:
                logger.info(f"No truck is fast enough to deliver package: {p_id}")
                return
            
        logger.info("Truck is fast enough") 


    def setCostObjective(self):
        """Function that sets the cost as objective function.

        Args:
            None
            
        Returns:
            None

        """

        logger.info("Setting total cost as objective.")

        # self.truck_assigned = {}
        self.truck_start_time = {}
        self.truck_package_start_time = {}
        self.truck_arrival_time = {}
        self.truck_package_arrival_time = {}
        self.truck_max_stops = {}
        self.truck_package_stop = {}

        self.truck_costs = {}
        for t_id in self.model_input.all_trucks:

            truck_start_time_var = self.model.NewIntVar(0, self.max_start, f'truck_start_time[{t_id}]')
            self.truck_start_time[t_id] = truck_start_time_var

            truck_arrival_time_var = self.model.NewIntVar(0, self.max_deadline, f'truck_arrival_time[{t_id}]')
            self.truck_arrival_time[t_id] = truck_arrival_time_var

            truck_max_stop_var = self.model.NewIntVar(0, self.model_input.max_stops, f'truck_max_stop[{t_id}]')
            self.truck_max_stops[t_id] = truck_max_stop_var

            for p_id in self.model_input.all_packages:
                self.model.Add(self.truck_arrival_time[t_id] >= self.package_arrival_time[p_id]).OnlyEnforceIf(self.truck_to_packages[t_id, p_id])

                self.model.Add(self.truck_start_time[t_id] >= self.package_start_time[p_id]).OnlyEnforceIf(self.truck_to_packages[t_id, p_id])
 
                self.model.Add(self.truck_max_stops[t_id] >= self.package_stops[p_id]).OnlyEnforceIf(self.truck_to_packages[t_id, p_id])
  
            truck_cost_var = self.model.NewIntVar(0, 
                                                    self.max_deadline * int(self.model_input.all_trucks[t_id].type.speed * self.model_input.all_trucks[t_id].type.cost_per_km / 1000 * self.model_input.cost_scale_factor) +
                                                    self.model_input.stop_cost * self.model_input.cost_scale_factor * (self.model_input.max_stops - 1), 
                                                    f'truck_cost[{t_id}]')
            self.truck_costs[t_id] = truck_cost_var

            truck_max_stop_equal_0 = self.model.NewBoolVar(f'truck_max_stop_equal_0[{t_id}]')

            self.model.Add(self.truck_max_stops[t_id] == 0).OnlyEnforceIf(truck_max_stop_equal_0)
            self.model.Add(self.truck_max_stops[t_id] != 0).OnlyEnforceIf(truck_max_stop_equal_0.Not())

            self.model.Add(truck_cost_var == (self.truck_arrival_time[t_id] - self.truck_start_time[t_id] - (self.truck_max_stops[t_id]-1) * self.model_input.stop_time
                                        ) *  int(self.model_input.all_trucks[t_id].type.speed * self.model_input.all_trucks[t_id].type.cost_per_km / 1000
                                          * self.model_input.cost_scale_factor) +  (self.truck_max_stops[t_id]-1) * self.model_input.stop_cost 
                                          * self.model_input.cost_scale_factor 
                        ).OnlyEnforceIf(truck_max_stop_equal_0.Not())

            self.model.Add(truck_cost_var == 0).OnlyEnforceIf(truck_max_stop_equal_0)

        # The cost should be as least as possible
        self.model.Minimize(sum(self.truck_costs[t_id] for t_id in self.model_input.all_trucks))

        self.countVariables()


    def setPackageTruckAssignmentConstraint(self):
        '''
        Pacakge need to be assigned to one truck exactly

        ''' 
        logger.info("Adding package to truck assignment constraint.")

        # Pacakge need to be assigned to one truck exactly
        for p_id in self.model_input.all_packages:
            self.model.Add(sum(self.truck_to_packages[t_id, p_id] for t_id in self.model_input.all_trucks) == 1)

        multiply_t_p1_p2_dict = {}

        all_t_ids = []
        i = 1
        for t_id in self.model_input.all_trucks:
            all_t_ids.append((t_id, i))
            i+=1

        # if two packages have differnet sources, they cannot be assigned to the same truck
        for p_id_1, p_id_2 in self.same_truck_packages:
            package_1 = self.model_input.all_packages[p_id_1]
            package_2 = self.model_input.all_packages[p_id_2]
            if package_1.source != package_2.source:
                for t_id in all_trucks:
                    self.model.Add(self.truck_to_packages[t_id, p_id_1] + self.truck_to_packages[t_id, p_id_2] <= 1)
                
                self.model.Add(self.same_truck_packages[p_id_1, p_id_2] == 0)

            self.model.Add(sum(self.truck_to_packages[t_id, p_id_1]*i for t_id, i in all_t_ids) 
                    == (sum(self.truck_to_packages[t_id, p_id_2]*i for t_id, i in all_t_ids))).OnlyEnforceIf(
                    self.same_truck_packages[p_id_1, p_id_2])

            self.model.Add(sum(self.truck_to_packages[t_id, p_id_1]*i for t_id, i in all_t_ids) 
                    != (sum(self.truck_to_packages[t_id, p_id_2]*i for t_id, i in all_t_ids))).OnlyEnforceIf(
                    self.same_truck_packages[p_id_1, p_id_2].Not())

        
        self.countVariables()


    def setPackageStartTimeConstraint(self):
        '''
        The start time of the truck should be greater or equal to the maximum available time of the packages in the same truck.

        '''
        logger.info("Adding truck start time constraint.")

        for p_id in self.model_input.all_packages:
            package = self.model_input.all_packages[p_id]
            # if package start time is larger or equal to its available time
            self.model.Add(self.package_start_time[p_id] >= package.available_time)


        for p_id_1, p_id_2 in self.same_truck_packages:
            package_1 = self.model_input.all_packages[p_id_1]
            package_2 = self.model_input.all_packages[p_id_2]
            # if packages are in the same truck, the start time should be the maximum one.
            self.model.Add(self.package_start_time[p_id_1] >= package_2.available_time).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2])
            self.model.Add(self.package_start_time[p_id_2] >= package_1.available_time).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2])            

        self.countVariables()
    
    def setFixedSrcConstraint(self):
        '''
        Assume all trucks start from the same location.

        '''
        sources = set()

        logger.info("Adding truck fix source constraint.")

        for index, package in self.model_input.all_packages.items():
            sources.add(package.source)
        
        assert(len(sources)==1)
            
        self.countVariables()

    def setPackageArrivalTimeConstraint(self):
        '''
        The package should be assigned to exactly one truck and delivered on-time.

        '''

        logger.info("Adding package arrival time constraint.")

        self.package_arrival_time = {}

        for p_id in self.model_input.all_packages:
            arrival_time_var = self.model.NewIntVar(self.min_start, self.max_deadline, f'arrival_time_[{p_id}]')
            self.package_arrival_time[p_id] = arrival_time_var

        self.trucks_with_type = collections.defaultdict(list)
        for t_id in self.model_input.all_trucks:            
            self.trucks_with_type[self.model_input.all_trucks[t_id].type.id].append(t_id)

        self.package_truck_type = {}
        for p_id in self.model_input.all_packages:
            for truck_type in self.model_input.truck_types:
                package_truck_type_var = self.model.NewBoolVar(f'package_truck_type_[{p_id, truck_type.id}]')
                self.package_truck_type[p_id, truck_type.id] = package_truck_type_var

                self.model.Add(sum(self.truck_to_packages[t_id, p_id] for t_id in self.trucks_with_type[truck_type.id]) == 1
                                ).OnlyEnforceIf(self.package_truck_type[p_id, truck_type.id])
                self.model.Add(sum(self.truck_to_packages[t_id, p_id] for t_id in self.trucks_with_type[truck_type.id]) == 0
                                ).OnlyEnforceIf(self.package_truck_type[p_id, truck_type.id].Not())

            # One package can be assigned to exactly one truck type
            self.model.Add(sum(self.package_truck_type[p_id, truck_type.id] for truck_type in self.model_input.truck_types) == 1)


        self.countVariables()

        self.p1_before_p2 = {}

        # Package arrival time should larger than the time from the source to package destination.
        for p_id, package in self.model_input.all_packages.items():
            self.model.Add(self.package_arrival_time[p_id] >= 
                sum(int(self.model_input.distance_matrix[package.source][package.destination] / truck_type.speed) 
                * self.package_truck_type[p_id, truck_type.id] for truck_type in self.model_input.truck_types)
                + self.package_start_time[p_id])

        for p_id_1, p_id_2 in self.same_truck_packages:
            package_1 = self.model_input.all_packages[p_id_1]
            package_2 = self.model_input.all_packages[p_id_2]

            # If two packages are in the same truck, they share the same truck type
            for truck_type in self.model_input.truck_types:
                self.model.Add(self.package_truck_type[p_id_1, truck_type.id] == self.package_truck_type[p_id_2, truck_type.id]
                ).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2])


            if package_1.destination == package_2.destination:
                # same arrival time       
                self.model.Add(self.package_arrival_time[p_id_1] == self.package_arrival_time[p_id_2]).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2])
                # same stop 
                self.model.Add(self.package_stops[p_id_1] == self.package_stops[p_id_2]).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2])
            else:
                # cannot be the same stop 
                self.model.Add(self.package_stops[p_id_1] != self.package_stops[p_id_2]).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2])

                p1_before_p2_var = self.model.NewBoolVar(f'p1_before_p2[{p_id_1}, {p_id_2}]')

                self.p1_before_p2[p_id_1, p_id_2] = p1_before_p2_var

                self.model.Add(self.package_stops[p_id_1] < self.package_stops[p_id_2]).OnlyEnforceIf(p1_before_p2_var)  
                self.model.Add(self.package_stops[p_id_1] >= self.package_stops[p_id_2]).OnlyEnforceIf(p1_before_p2_var.Not())

                # If p1 and p2 in the same truck and p1 stop first
                self.model.Add(self.package_arrival_time[p_id_2] >= 
                    sum(int(self.model_input.distance_matrix[package_1.destination][package_2.destination] / truck_type.speed)
                    * self.package_truck_type[p_id_2, truck_type.id] for truck_type in self.model_input.truck_types)
                    + self.package_arrival_time[p_id_1] + self.model_input.stop_time).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2],
                    p1_before_p2_var)

                # If p1 and p2 in the same truck and p2 stop first
                self.model.Add(self.package_arrival_time[p_id_1] >= 
                    sum(int(self.model_input.distance_matrix[package_2.destination][package_1.destination] / truck_type.speed)
                    * self.package_truck_type[p_id_1, truck_type.id] for truck_type in self.model_input.truck_types)
                    + self.package_arrival_time[p_id_2] + self.model_input.stop_time).OnlyEnforceIf(self.same_truck_packages[p_id_1, p_id_2],
                    p1_before_p2_var.Not())                 


        # package arrival time shoud be less than the deadline
        for p_id in self.model_input.all_packages:
            self.model.Add(self.package_arrival_time[p_id] <= self.model_input.all_packages[p_id].deadline)

        self.countVariables()


    def setTruckVolumeCapacityConstraint(self):
        '''
        The total volume of the packages cannot exceed the capacity of the truck.
        '''

        logger.info("Adding truck volume capacity constraint.")

        for t_id in self.model_input.all_trucks:
            self.model.Add(sum(self.truck_to_packages[t_id, p_id]*self.model_input.all_packages[p_id].area 
                for p_id in self.model_input.all_packages)
                <= self.model_input.all_trucks[t_id].type.area_capacity)
        self.countVariables()

    def setTruckWeightCapacityConstraint(self):
        '''
        The total weight of the packages cannot exceed the capacity of the truck.
        '''
        logger.info("Adding truck weight capacity constraint.")

        for t_id in self.model_input.all_trucks:
            self.model.Add(sum(self.truck_to_packages[t_id, p_id]*self.model_input.all_packages[p_id].weight for p_id in self.model_input.all_packages)
                <= self.model_input.all_trucks[t_id].type.weight_capacity)
        self.countVariables()

    def setDangerTypeConstraint(self):
        '''
        Dangerouse packages with different danger types cannot be put on the same truck. 
        '''

        logger.info("Adding danger type constraint.")

        for p_id_1, p_id_2 in self.same_truck_packages:
            # If neither one is "non_danger" type of package
            if self.model_input.all_packages[p_id_1].danger_type != 'non_danger' and self.model_input.all_packages[p_id_2].danger_type != 'non_danger':
                self.model.Add(self.model_input.all_packages[p_id_1].danger_type == self.model_input.all_packages[p_id_2].danger_type).OnlyEnforceIf(
                self.same_truck_packages[p_id_1, p_id_2])

                if self.model_input.all_packages[p_id_1].danger_type != self.model_input.all_packages[p_id_2].danger_type:
                    self.model.Add(self.same_truck_packages[p_id_1, p_id_2]==0)

        self.countVariables()

    def setPackageTimeWindowConstraint(self):
        '''
        The maximum available time should be not greater than the minmum available time + X hours for all packages in the same truck.
        '''
        logger.info("Adding package time window constraint.")

        for p_id_1, p_id_2 in self.same_truck_packages:    

            package1 = self.model_input.all_packages[p_id_1]
            package2 = self.model_input.all_packages[p_id_2]

            if abs(package1.available_time - package2.available_time) > self.model_input.max_time_difference_between_package:
                self.model.Add(self.same_truck_packages[p_id_1, p_id_2] == 0)                                
            
        self.countVariables()