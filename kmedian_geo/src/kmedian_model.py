import pandas as pd
from pyomo.environ import *


def create_abstract_model(k, enable_min_max_elements, enable_max_demand):

    model = AbstractModel(name="Network Flows Abstract Model")

    model.store_facility_allocation_var_input_set = Set(dimen=2)
    model.facility_selection_var_input_set = Set(dimen=1)
    model.stores_set = Set(dimen=1)
    model.facilities_set = Set(dimen=1)

    model.costs = Param(model.store_facility_allocation_var_input_set, within=Any)
    model.facility_min_elements = Param(model.facilities_set, within=Any)
    model.facility_max_elements = Param(model.facilities_set, within=Any)
    model.store_demand = Param(model.stores_set, within=Any)
    model.facility_maximum_demand = Param(model.facilities_set, within=Any)
    model.k = Param(within=Any)

    # create variables
    model.store_facility_allocation_var = Var(model.store_facility_allocation_var_input_set, within=Binary)
    model.facility_selection_var = Var(model.facility_selection_var_input_set, within=Binary)

    # model objective
    def obj_rule(model):
        return sum(model.costs[store, facility] * model.store_facility_allocation_var[store, facility] \
                   for store, facility in model.store_facility_allocation_var_input_set)

    model.obj = Objective(rule=obj_rule, sense=minimize)

    # each store is allocated to one facility
    def store_allocation_rule(model, store):
        return sum(model.store_facility_allocation_var[store, facility] \
                   for facility in model.facilities_set) == 1

    model.store_allocation = Constraint(model.stores_set, rule=store_allocation_rule)

    # k number of facilities is selected
    def k_facilities_rule(model):
        return sum(model.facility_selection_var[facility] \
                   for facility in model.facilities_set) == k

    model.k_facilities = Constraint([], rule=k_facilities_rule)

    # store can not allocated if facility is not selected
    def store_enablement_rule(model, store, facility):
        return model.store_facility_allocation_var[store, facility] <= model.facility_selection_var[facility]

    model.store_enablement = Constraint(model.store_facility_allocation_var_input_set, rule=store_enablement_rule)

    if enable_min_max_elements:
        # minimum elements in facility
        def min_stores_rule(model, facility):
            return sum(model.store_facility_allocation_var[store, facility] \
                       for store in model.stores_set) >= model.facility_min_elements[facility]

        model.min_stores = Constraint(model.facilities_set, rule=min_stores_rule)

        # maximum elements in facility
        def max_stores_rule(model, facility):
            return sum(model.store_facility_allocation_var[store, facility] \
                       for store in model.stores_set) >= model.facility_max_elements[facility]

        model.max_stores = Constraint(model.facilities_set, rule=max_stores_rule)

    # maximum demand in facility
    if enable_max_demand:
        def max_demand_rule(model, facility):
            return sum(model.store_demand[store] * model.store_facility_allocation_var[store, facility]
                       for store in model.stores_set) <= model.facility_maximum_demand[facility]

        model.max_demand = Constraint(model.facilities_set, rule=max_demand_rule)

    return model

def create_model_instance(model,
                          store_facility_allocation_var_input_set,
                          facility_selection_var_input_set,
                          stores_set,
                          facilities_set,
                          costs,
                          facility_min_elements,
                          facility_max_elements,
                          store_demand,
                          facility_maximum_demand,
                          k
                          ):

    data = {None: {
        'store_facility_allocation_var_input_set': {None: store_facility_allocation_var_input_set},
        'facility_selection_var_input_set': {None: facility_selection_var_input_set},
        'stores_set': {None: stores_set},
        'facilities_set': {None: facilities_set},
        'costs': costs,
        'facility_min_elements': facility_min_elements,
        'facility_max_elements': facility_max_elements,
        'store_demand': store_demand,
        'facility_maximum_demand': facility_maximum_demand,
    },
        'k': k}

    model_instance = model.create_instance(data)

    return model_instance

def solve_model(model_instance,
                mip_gap,
                solver_time_limit_mins,
                solver='GLPK'):

    if solver=='GLPK':
        # initiate GLPK
        optimize = SolverFactory('glpk')
        optimize.options["mipgap"] = mip_gap
        optimize.options['tmlim'] = 60 * solver_time_limit_mins

    # solves and updates variables
    solution = optimize.solve(model_instance)

    return solution

def get_results(solution, model_instance, costs):

    if solution.solver.termination_condition == TerminationCondition.optimal:
        print('Optimal solution is found')

        print('Objective value = {}'.format(str(model_instance.obj.expr())))

        solution_store_facility_allocation = pd.Series(
            model_instance.store_facility_allocation_var.get_values()).reset_index()
        solution_store_facility_allocation.rename(columns={'level_0': 'STORE', 'level_1': 'FACILITY', 0: 'VALUE'},
                                                  inplace=True)
        solution_store_facility_allocation = solution_store_facility_allocation[
            solution_store_facility_allocation['VALUE'] != 0]

        solution_costs = pd.Series(costs).reset_index()
        solution_costs.rename(columns={'level_0': 'STORE', 'level_1': 'FACILITY', 0: 'COST'},
                              inplace=True)

        solution_store_facility_allocation = solution_store_facility_allocation.merge(solution_costs,
                                                                                      how='left',
                                                                                      on=['STORE', 'FACILITY'])

        return solution_store_facility_allocation

    elif solution.solver.termination_condition == TerminationCondition.infeasible:
        raise Exception('Infeasible solution')
    elif solution.solver.termination_condition == TerminationCondition.unbounded:
        raise Exception('Unbounded solution')
    else:
        raise Exception('Solver Status: {}'.format(str(solution.solver.status)))
