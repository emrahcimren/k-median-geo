import pandas as pd
from kmedian_geo.src import kmedian_inputs as kmi
from kmedian_geo.src import kmedian_model as pyo


def run_kmedian(stores,
                facilities,
                costs,
                k_list,
                enable_maximum_demand_at_facility=False,
                mip_gap=0.01,
                solver_time_limit_mins=2,
                solver='GLPK',
                ):
    """
    Running k-median model
    Args:
        stores ():
        facilities ():
        costs ():
        k_list ():
        enable_maximum_demand_at_facility ():
        mip_gap ():
        solver_time_limit_mins ():
        solver (): 'GLPK', 'CBC'

    Returns:

    """

    print('getting model inputs')
    mi = kmi.ModelInputs(stores,
                         facilities,
                         costs)

    print('formulating the abstract model')
    model = pyo.create_abstract_model(enable_maximum_demand_at_facility)

    print('getting model instance')
    model_instance = pyo.create_model_instance(model,
                                               mi.store_facility_allocation_var_input_set,
                                               mi.facility_selection_var_input_set,
                                               mi.store_set,
                                               mi.facility_set,
                                               mi.facilities_by_stores_set,
                                               mi.stores_by_facilities_set,
                                               mi.costs,
                                               mi.facility_min_elements,
                                               mi.facility_max_elements,
                                               mi.store_demand,
                                               mi.facility_maximum_demand
                                               )

    print('running model for each k \n')
    final_results = []
    for k in k_list:

        print('running for K = {} \n'.format(str(k)))

        print('setting k')
        model_instance.k.value = k

        print('solving the model')
        solution = pyo.solve_model(model_instance,
                                   mip_gap,
                                   solver_time_limit_mins,
                                   solver)

        print('getting results')
        solution_store_facility_allocation = pyo.get_results(solution, model_instance, costs)
        final_results.append(solution_store_facility_allocation)

    final_results = pd.concat(final_results)

    return final_results
