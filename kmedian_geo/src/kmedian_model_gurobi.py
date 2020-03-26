import pandas as pd
from gurobipy import *


class ModelGurobi:

    def __init__(self,
                 stores_set,
                 facilities_set,
                 store_facility_allocation_var_input_set,
                 facility_selection_var_input_set,
                 facility_min_elements,
                 facility_max_elements,
                 facility_maximum_demand,
                 store_demand,
                 costs
                 ):

        self.stores_set = stores_set
        self.facilities_set = facilities_set
        self.store_facility_allocation_var_input_set = store_facility_allocation_var_input_set
        self.facility_selection_var_input_set = facility_selection_var_input_set
        self.facility_min_elements = facility_min_elements
        self.facility_max_elements = facility_max_elements
        self.facility_maximum_demand = facility_maximum_demand
        self.store_demand = store_demand
        self.costs = costs

        self.solver = None
        self.store_facility_allocation_var = None
        self.facility_selection_var = None

        self.solution = None
        self.store_facility_allocation_solution = None
        self.facility_selection_solution = None

    def formulate_model(self, k, enable_min_max_elements, enable_max_demand):
        '''
        Formulate Gurobi model
        :param k:
        :param enable_min_max_elements:
        :param enable_max_demand:
        :return:
        '''

        self.solver = Model("Source to Destination Allocation")

        self.store_facility_allocation_var = self.solver.addVars(self.store_facility_allocation_var_input_set, name="x")
        self.facility_selection_var = self.solver.addVars(self.facility_selection_var_input_set, vtype=GRB.BINARY, name="y")

        # Objective
        objective = LinExpr()

        # transportation cost
        for store, facility in self.store_facility_allocation_var_input_set:
            objective += (
                    self.costs[store, facility] * self.store_facility_allocation_var[store, facility]
            )
        self.solver.setObjective(objective)

        # each store is allocated to one facility
        self.solver.addConstrs(
            (
                self.store_facility_allocation_var.sum(store, "*") == 1
                for store in self.stores_set
            ),
            "each store is allocated to one facility",
        )

        # k number of facilities is selected
        self.solver.addConstr(
            (
                self.facility_selection_var.sum("*") == k
            ),
            "k number of facilities is selected",
        )

        # store can not allocated if facility is not selected
        self.solver.addConstrs(
            (
                self.store_facility_allocation_var[store, facility] <= self.facility_selection_var[facility]
                for store, facility in self.store_facility_allocation_var_input_set
            ),
            "store can not allocated if facility is not selected",
        )

        if enable_min_max_elements:
            # minimum elements in facility
            self.solver.addConstrs(
                (
                    self.store_facility_allocation_var["*", facility] >= self.facility_min_elements[facility]
                    for facility in self.facilities_set
                ),
                "minimum elements in facility"
            )

            # maximum elements in facility
            self.solver.addConstrs(
                (
                    self.store_facility_allocation_var["*", facility] <= self.facility_max_elements[facility]
                    for facility in self.facilities_set
                ),
                "maximum elements in facility"
            )

        # maximum demand in facility
        if enable_max_demand:
            for facility in self.facilities_set:
                self.solver.addConstr(quicksum(
                    self.store_demand[store] * self.store_facility_allocation_var[store, facility] for store in
                    self.stores_set) <=
                                    self.facility_maximum_demand[facility])

    def solve_model(self,
                    mip_gap,
                    solver_time_limit_mins):
        '''
        Solver model
        :param mip_gap:
        :param solver_time_limit_mins:
        :return:
        '''

        self.solver.Params.MIPGap = mip_gap
        self.solver.Params.TimeLimit = 60 * solver_time_limit_mins

        self.solver.modelSense = GRB.MINIMIZE
        self.solver.optimize()

    def get_results(self):
        '''
        Get solution
        :return:
        '''

        # get solution
        if self.solver.status == GRB.Status.OPTIMAL:

            store_facility_allocation_solution = self.solver.getAttr("x", self.store_facility_allocation_var)
            store_facility_allocation_solution = pd.Series(store_facility_allocation_solution).reset_index()
            store_facility_allocation_solution.columns = [
                "STORE",
                "FACILITY",
                "VALUE",
            ]
            self.store_facility_allocation_solution = store_facility_allocation_solution[store_facility_allocation_solution['VALUE'] != 0]

            facility_selection_solution = self.solver.getAttr("x", self.facility_selection_var)
            facility_selection_solution = pd.Series(facility_selection_solution).reset_index()
            facility_selection_solution.columns = [
                "FACILITY",
                "VALUE",
            ]
            self.facility_selection_solution = facility_selection_solution[facility_selection_solution['VALUE'] != 0]

        else:
            raise Exception('No solution exists')
