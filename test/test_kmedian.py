'''
Test class for testing kmeans
'''

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'kmedian_geo')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'kmedian_geo/src')))

from kmedian_geo.src import kmedian_inputs_ortools as kmi
from kmedian_geo import kmedian as km
from kmedian_geo.src import data

stores = data.test_stores_data
facilities = data.test_facilities_data
costs = data.test_cost_data


class KMedianTest(unittest.TestCase):

    def test_kmedian_inputs(self):
        '''
        Test for core_model_inputs
        :return:
        '''

        mi = kmi.ModelInputs(stores,
                             facilities,
                             costs)

        self.assertTrue(len(mi.store_facility_allocation_var_input) > 0)

    def test_run_kmedian_model_ortools(self):
        '''
        Test for core model formulation
        :return:
        '''

        k = 2
        store_facility_allocation_solution, facility_selection_solution = km.run_kmedian_or_tools_model(stores,
                                                                                                        facilities,
                                                                                                        costs,
                                                                                                        k,
                                                                                                        enable_min_max_elements=False,
                                                                                                        enable_max_demand=False,
                                                                                                        mip_gap=0.01,
                                                                                                        solver_time_limit_mins=2,
                                                                                                        write_lp=False)

        self.assertTrue(len(store_facility_allocation_solution) > 0)


if __name__ == '__main__':
    unittest.main()
