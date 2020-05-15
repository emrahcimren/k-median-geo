import pandas as pd
import logging
from pathlib import Path
from datetime import datetime as dt
from kmedian_geo.src import kmedian_inputs as kmi
from kmedian_geo.src import kmedian_model as pyo
from kmedian_geo.src import logger as ls


def run_kmedian(stores,
                facilities,
                costs,
                k_list,
                enable_maximum_demand_at_facility=False,
                mip_gap=0.01,
                solver_time_limit_mins=2,
                solver='GLPK',
                threads=8,
                cbc_scip_solver_path=None,
                save_model_as_lp=False,
                log_path='k_median_logs'
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
        solver (): 'GLPK', 'CBC', 'SCIP'
        threads (): Number of cores used
        cbc_scip_solver_path (): cnc scip solver path
        save_model_as_lp (): save model as lp
        log_path (): logger path

    Returns:

    """

    logging_file_path = r"{}".format(log_path)
    run_id = dt.now().strftime("%Y-%m-%d %H:%M:%S").replace(" ", "__").replace(":", "_")
    log_file_name = '_'

    Path('{}\debug'.format(log_path)).mkdir(parents=True, exist_ok=True)
    ls.set_logger(run_id, logging_file_path, log_file_name)

    logging.debug('getting model inputs')
    mi = kmi.ModelInputs(stores,
                         facilities,
                         costs)

    logging.debug('formulating the abstract model')
    model = pyo.create_abstract_model(enable_maximum_demand_at_facility)

    logging.debug('getting model instance')
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
    if save_model_as_lp:
        model_instance.write('model.lp')

    logging.debug('running model for each k \n')
    final_results = []
    for k in k_list:

        logging.debug('running for K = {} \n'.format(str(k)))

        logging.debug('Cloning model instance')
        #model_instance_for_solution = model_instance.clone()

        logging.debug('setting k')
        model_instance.k.value = k

        logging.debug('solving the model')
        solution = pyo.solve_model(model_instance,
                                   mip_gap,
                                   solver_time_limit_mins,
                                   solver,
                                   threads,
                                   cbc_scip_solver_path)

        logging.debug('getting results')
        solution_store_facility_allocation = pyo.get_results(solution, model_instance, costs)
        final_results.append(solution_store_facility_allocation)

    final_results = pd.concat(final_results)

    return final_results
