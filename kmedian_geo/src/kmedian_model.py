import pandas as pd
from pyomo.environ import *


def create_abstract_model(enable_min_max_elements,
                          enable_max_demand):
    """
    Create the abstract model
    Args:
        enable_min_max_elements ():
        enable_max_demand ():

    Returns:

    """

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
    model.k = Param(initialize=1, mutable=True)

    # create variables
    model.store_facility_allocation_var = Var(model.store_facility_allocation_var_input_set, within=Binary)
    model.facility_selection_var = Var(model.facility_selection_var_input_set, within=Binary)

    # model objective
    def obj_rule(model):
        """
        Objective function
        Args:
            model ():

        Returns:

        """
        return summation(model.costs, model.store_facility_allocation_var)

    model.obj = Objective(rule=obj_rule, sense=minimize)

    # each store is allocated to one facility
    def store_allocation_rule(model, store):
        """
        Each store assigns to one facility
        Args:
            model ():
            store ():

        Returns:

        """
        return quicksum(model.store_facility_allocation_var[store, :]) == 1

    model.store_allocation = Constraint(model.stores_set, rule=store_allocation_rule)

    # k number of facilities is selected
    def k_facilities_rule(model):
        """
        Select k facilities
        Args:
            model ():

        Returns:

        """
        return quicksum(model.facility_selection_var[:]) == model.k

    model.k_facilities = Constraint(rule=k_facilities_rule)

    # store can not allocated if facility is not selected
    def store_enablement_rule(model, store, facility):
        """
        Enable allocation if site is selected
        Args:
            model (): 
            store (): 
            facility (): 

        Returns:

        """

        return model.store_facility_allocation_var[store, facility] <= model.facility_selection_var[facility]

    model.store_enablement = Constraint(model.store_facility_allocation_var_input_set, rule=store_enablement_rule)

    if enable_min_max_elements:
        # minimum elements in facility
        def min_stores_rule(model, facility):
            """
            Minimum stores assigned
            Args:
                model ():
                facility ():

            Returns:

            """
            return quicksum(model.store_facility_allocation_var[:, facility]) >= model.facility_min_elements[facility]

        model.min_stores = Constraint(model.facilities_set, rule=min_stores_rule)

        # maximum elements in facility
        def max_stores_rule(model, facility):
            """
            Max stores assigned
            Args:
                model ():
                facility ():

            Returns:

            """
            return quicksum(model.store_facility_allocation_var[:, facility]) >= model.facility_max_elements[facility]

        model.max_stores = Constraint(model.facilities_set, rule=max_stores_rule)

    # maximum demand in facility
    if enable_max_demand:
        def max_demand_rule(model, facility):
            """
            Max demand rule
            Args:
                model ():
                facility ():

            Returns:

            """
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
                          facility_maximum_demand
                          ):
    """
    Create model instance
    Args:
        model ():
        store_facility_allocation_var_input_set ():
        facility_selection_var_input_set ():
        stores_set ():
        facilities_set ():
        costs ():
        facility_min_elements ():
        facility_max_elements ():
        store_demand ():
        facility_maximum_demand ():

    Returns:

    """

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
    }}

    model_instance = model.create_instance(data)

    return model_instance


def solve_model(model_instance,
                mip_gap,
                solver_time_limit_mins,
                solver='GLPK'):
    """
    Solve model
    Args:
        model_instance ():
        mip_gap ():
        solver_time_limit_mins ():
        solver ():

    Returns:

    """

    if solver=='GLPK':
        # initiate GLPK
        optimize = SolverFactory('glpk')
        optimize.options["mipgap"] = mip_gap
        optimize.options['tmlim'] = 60 * solver_time_limit_mins

    # solves and updates variables
    solution = optimize.solve(model_instance)

    return solution


def get_results(solution, model_instance, costs):
    """
    Get model results
    Args:
        solution ():
        model_instance ():
        costs ():

    Returns:

    """

    if solution.solver.termination_condition == TerminationCondition.optimal:
        print('Optimal solution is found')

        print('Objective value = {}'.format(str(model_instance.obj.expr())))

        solution_store_facility_allocation = pd.Series(
            model_instance.store_facility_allocation_var.get_values()).reset_index()
        solution_store_facility_allocation.rename(columns={'level_0': 'STORE', 'level_1': 'FACILITY', 0: 'VALUE'},
                                                  inplace=True)
        solution_store_facility_allocation = solution_store_facility_allocation[
            solution_store_facility_allocation['VALUE'] != 0]

        solution_costs = costs.copy()
        solution_costs.rename(columns={'FACILITY_NAME': 'FACILITY', 'LOCATION_NAME': 'STORE'}, inplace=True)
        solution_store_facility_allocation = solution_store_facility_allocation.merge(solution_costs,
                                                                                      how='left',
                                                                                      on=['STORE', 'FACILITY'])
        solution_store_facility_allocation['K'] = model_instance.k.value

        return solution_store_facility_allocation

    elif solution.solver.termination_condition == TerminationCondition.infeasible:
        raise Exception('Infeasible solution')
    elif solution.solver.termination_condition == TerminationCondition.unbounded:
        raise Exception('Unbounded solution')
    else:
        raise Exception('Solver Status: {}'.format(str(solution.solver.status)))
