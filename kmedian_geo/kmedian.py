from kmedian_geo.src import kmedian_inputs as kmi


def run_kmedian_or_tools_model(stores,
                               facilities,
                               costs,
                               k,
                               enable_min_max_elements=False,
                               enable_max_demand=False,
                               mip_gap=0.01,
                               solver_time_limit_mins=2,
                               write_lp=False):
    '''
    Run kmeans OR Tools model
    :param stores:
    :param facilities:
    :param costs:
    :param k:
    :param enable_min_max_elements:
    :param mip_gap:
    :param solver_time_limit_mins:
    :param write_lp:
    :return:
    '''

    from kmedian_geo.src import kmedian_model_ortools as ort

    mi = kmi.ModelInputs(stores,
                         facilities,
                         costs)

    model = ort.Model(mi.store_set,
                      mi.facility_set,
                      mi.store_facility_allocation_var_input_set,
                      mi.facility_selection_var_input_set,
                      mi.facility_min_elements,
                      mi.facility_max_elements,
                      mi.facility_maximum_demand,
                      mi.store_demand,
                      mi.costs)

    model.formulate_model(k,
                          enable_min_max_elements,
                          enable_max_demand)

    model.solve_model(mip_gap,
                      solver_time_limit_mins,
                      write_lp)

    model.get_results()

    return model.store_facility_allocation_solution, model.facility_selection_solution
