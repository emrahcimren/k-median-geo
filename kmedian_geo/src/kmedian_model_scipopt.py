import pandas as pd
from pyscipopt import Model
from pyscipopt import quicksum


class ModelScipopt:

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
        Formulate Scipopt model
        :param k:
        :param enable_min_max_elements:
        :param enable_max_demand:
        :return:
        '''

        self.solver = Model("kmedian")

        self.store_facility_allocation_var = {}
        for store, facility in self.store_facility_allocation_var_input_set:
            self.store_facility_allocation_var[store, facility] = self.solver.addVar(vtype="B",
                                                                                     name="x{}{}".format(store,
                                                                                                         facility))

        self.facility_selection_var = {}
        for facility in self.facility_selection_var_input_set:
            self.facility_selection_var[facility] = self.solver.addVar(vtype="B", name="y{}".format(facility))

        # each store is allocated to one facility
        for store in self.stores_set:
            self.solver.addCons(
                quicksum(self.store_facility_allocation_var[store, facility] for facility in self.facilities_set) == 1,
                "Store allocation{}".format(store))

        # k number of facilities is selected
        self.solver.addCons(quicksum(self.facility_selection_var[facility] for facility in self.facilities_set) == k,
                            "k")

        # store can not allocated if facility is not selected
        for store, facility in self.store_facility_allocation_var_input_set:
            self.solver.addCons(
                self.store_facility_allocation_var[store, facility] <= self.facility_selection_var[facility],
                "Strong{},{}".format(store, facility))

        if enable_min_max_elements:
            # minimum elements in facility
            for facility in self.facilities_set:
                self.solver.addCons(
                    quicksum(self.store_facility_allocation_var[store, facility] for store in self.stores_set) >=
                    self.facility_min_elements[facility], "min elements{}".format(facility))
                self.solver.addCons(
                    quicksum(self.store_facility_allocation_var[store, facility] for store in self.stores_set) <=
                    self.facility_max_elements[facility], "max elements{}".format(facility))

        # maximum demand in facility
        if enable_max_demand:
            for facility in self.facilities_set:
                self.solver.addCons(quicksum(
                    self.store_demand[store] * self.store_facility_allocation_var[store, facility] for store in
                    self.stores_set) <=
                                    self.facility_maximum_demand[facility], "max demand{}".format(facility))

        self.solver.setObjective(
            quicksum(self.costs[store, facility] * self.store_facility_allocation_var[store, facility]
                     for store, facility in self.store_facility_allocation_var_input_set),
            "minimize")

    def solve_model(self,
                    mip_gap,
                    solver_time_limit_mins):
        '''
        Solver model
        :param mip_gap:
        :param solver_time_limit_mins:
        :return:
        '''

        self.solver.setRealParam('limits/gap', mip_gap)
        self.solver.setRealParam('limits/time', 60 * solver_time_limit_mins)
        self.solver.optimize()
        print('Number of variables in model = {}'.format(str(self.solver.getNVars())))
        print('Number of constraints in model = {}'.format(str(self.solver.getNConss())))

    def get_results(self):
        '''
        Get solution
        :return:
        '''

        if self.solver.getStatus() == "optimal":
            print("Optimal value:", self.solver.getObjVal())

            store_facility_allocation_solution = []
            for store, facility in self.store_facility_allocation_var_input_set:
                store_facility_allocation_solution.append({'STORE': store,
                                                           'FACILITY': facility,
                                                           'VALUE': self.solver.getVal(self.store_facility_allocation_var[store, facility])
                                                           })
            store_facility_allocation_solution = pd.DataFrame(store_facility_allocation_solution)
            self.store_facility_allocation_solution = store_facility_allocation_solution[
                store_facility_allocation_solution['VALUE'] != 0]

            facility_selection_solution = []
            for facility in self.facilities_set:
                facility_selection_solution.append({'FACILITY': facility,
                                                    'VALUE': self.solver.getVal(self.facility_selection_var[facility])
                                                    })
            facility_selection_solution = pd.DataFrame(facility_selection_solution)
            self.facility_selection_solution = facility_selection_solution[
                facility_selection_solution['VALUE'] != 0]

        else:
            raise Exception('No solution exists')
