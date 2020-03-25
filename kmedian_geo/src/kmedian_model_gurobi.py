import pandas as pd
import sys
from ortools.linear_solver import pywraplp


class Model:

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

    @staticmethod
    def _redirect_to_file(self, text):
        """ Write out the model in linear programming format.
        Parameters
        ----------
        text : str
            full lp formulation in str format
        """
        original = sys.stdout
        sys.stdout = open('kmedian_or_tools_model.lp', 'w')
        print(text)
        sys.stdout = original

    def formulate_model(self, k, enable_min_max_elements, enable_max_demand):
        '''
        Formulate OR Tools model
        :param k:
        :param enable_min_max_elements:
        :return:
        '''
        self.solver = pywraplp.Solver('SolveIntegerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        infinity = self.solver.infinity()

        self.store_facility_allocation_var = {}
        for store, facility in self.store_facility_allocation_var_input_set:
            self.store_facility_allocation_var[store, facility] = self.solver.NumVar(0, infinity,
                                                                                     'x[{}, {}]'.format(str(store),
                                                                                                        str(facility)))
        self.facility_selection_var = {}
        for facility in self.facility_selection_var_input_set:
            self.facility_selection_var[facility] = self.solver.BoolVar('y[{}]'.format(str(facility)))

        # each store is allocated to one facility
        for store in self.stores_set:
            self.solver.Add(
                self.solver.Sum([self.store_facility_allocation_var[store, facility]
                                 for facility in self.facilities_set]) == 1
            )

        # k number of facilities is selected
        self.solver.Add(
            self.solver.Sum([self.facility_selection_var[facility] for facility in self.facilities_set]) == k
        )

        # store can not allocated if facility is not selected
        for store, facility in self.store_facility_allocation_var_input_set:
            self.solver.Add(
                self.store_facility_allocation_var[store, facility] <= self.facility_selection_var[facility]
            )

        if enable_min_max_elements:
            # minimum elements in facility
            for facility in self.facilities_set:
                self.solver.Add(
                    self.solver.Sum([self.store_facility_allocation_var[store, facility]
                                     for store in self.stores_set]) >= self.facility_min_elements[facility]
                )

            # maximum elements in facility
            for facility in self.facilities_set:
                self.solver.Add(
                    self.solver.Sum([self.store_facility_allocation_var[store, facility]
                                     for store in self.stores_set]) <= self.facility_max_elements[facility]
                )

        # maximum demand in facility
        if enable_max_demand:
            for facility in self.facilities_set:
                self.solver.Add(
                    self.solver.Sum([self.store_demand[store] * self.store_facility_allocation_var[store, facility]
                                     for store in self.stores_set]) <= self.facility_maximum_demand[facility]
                )

        # add objective
        self.solver.Minimize(
            self.solver.Sum(
                [self.costs[store, facility] * self.store_facility_allocation_var[store, facility]
                 for store, facility in self.store_facility_allocation_var_input_set
                 ]
            )
        )

    def solve_model(self,
                    mip_gap,
                    solver_time_limit_mins,
                    write_lp):

        solver_parameters = pywraplp.MPSolverParameters()
        solver_parameters.SetDoubleParam(pywraplp.MPSolverParameters.RELATIVE_MIP_GAP, mip_gap)
        self.solver.SetTimeLimit(solver_time_limit_mins * 60 * 1000)
        self.solver.EnableOutput()
        self.solution = self.solver.Solve()

        print('Number of variables in model = {}'.format(str(self.solver.NumVariables())))
        print('Number of constraints in model = {}'.format(str(self.solver.NumConstraints())))

        if write_lp:
            lp_formulation = self.solver.ExportModelAsLpFormat(True)
            self._redirect_to_file(lp_formulation)

    def get_results(self):
        '''
        Get solution
        :return:
        '''

        # get solution
        if self.solution == pywraplp.Solver.OPTIMAL:
            print('Solution is found')
            print('Problem solved in {} milliseconds'.format(str(self.solver.WallTime())))
            print('Problem solved in {} iterations'.format(str(self.solver.Iterations())))
            print('Problem solved in {} iterations'.format(str(self.solver.Iterations())))
            print('Problem objective = {} '.format(str(self.solver.Objective().Value())))

            store_facility_allocation_solution = []
            for store, facility in self.store_facility_allocation_var_input_set:
                store_facility_allocation_solution.append({'STORE': store,
                                                           'FACILITY': facility,
                                                           'VALUE': self.store_facility_allocation_var[
                                                               store, facility].solution_value()
                                                           })
            self.store_facility_allocation_solution = pd.DataFrame(store_facility_allocation_solution)
            self.store_facility_allocation_solution = self.store_facility_allocation_solution[
                self.store_facility_allocation_solution['VALUE'] != 0]

            facility_selection_solution = []
            for facility in self.facilities_set:
                facility_selection_solution.append({'FACILITY': facility,
                                                    'VALUE': self.facility_selection_var[facility].solution_value()
                                                    })
            self.facility_selection_solution = pd.DataFrame(facility_selection_solution)
            self.facility_selection_solution = self.facility_selection_solution[
                self.facility_selection_solution['VALUE'] != 0]

        else:
            raise Exception('No solution exists')
