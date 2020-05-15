'''
Test class for testing kmeans
'''

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'kmedian_geo')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'kmedian_geo/src')))

from kmedian_geo.src import data

stores = data.test_stores_data
facilities = data.test_facilities_data
costs = data.test_cost_data


class KMedianTest(unittest.TestCase):

    def test_kmedian_inputs(self):
        """
        Test for core_model_inputs
        Returns:

        """
        from kmedian_geo.src import kmedian_inputs as kmi
        mi = kmi.ModelInputs(stores,
                             facilities,
                             costs)

        self.assertTrue(len(mi.store_facility_allocation_var_input) > 0)

    def test_run_kmedian_cbc(self):
        """
        Test for core model formulation
        Returns:

        """
        from kmedian_geo import kmedian as km
        k_list = [3]
        final_results = km.run_kmedian(stores,
                                       facilities,
                                       costs,
                                       k_list,
                                       mip_gap=0.01,
                                       solver_time_limit_mins=2,
                                       solver='CBC'
                                       )

        self.assertTrue(len(final_results) > 0)

    def test_run_kmedian_glpk(self):
        """
        Test for core model formulation
        Returns:

        """
        from kmedian_geo import kmedian as km
        k_list = [3]
        final_results = km.run_kmedian(stores,
                                       facilities,
                                       costs,
                                       k_list,
                                       mip_gap=0.01,
                                       solver_time_limit_mins=2,
                                       solver='GLPK'
                                       )

        self.assertTrue(len(final_results) > 0)

    def test_run_kmedian_scip(self):
        """
        Test for core model formulation
        Returns:

        """
        from kmedian_geo import kmedian as km
        k_list = [3]
        final_results = km.run_kmedian(stores,
                                       facilities,
                                       costs,
                                       k_list,
                                       mip_gap=0.01,
                                       solver_time_limit_mins=2,
                                       solver='SCIP'
                                       )

        self.assertTrue(len(final_results) > 0)


if __name__ == '__main__':
    unittest.main()
