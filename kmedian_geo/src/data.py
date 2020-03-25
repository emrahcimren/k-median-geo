import pandas as pd
import os
current_dir, this_filename = os.path.split(__file__)

stores = pd.read_pickle(os.path.join(current_dir, '../data/stores.pkl'))
facilities = pd.read_pickle(os.path.join(current_dir, '../data/facilities.pkl'))
costs = pd.read_pickle(os.path.join(current_dir, '../data/costs.pkl'))

stores_list = ['store_15015', 'store_15027', 'store_15050', 'store_15071', 'store_15112']
facilities_list = ['facility_15001', 'facility_15003', 'facility_15009']

test_stores_data = stores[stores['LOCATION_NAME'].isin(stores_list)]
test_facilities_data = facilities[facilities['FACILITY_NAME'].isin(facilities_list)]
test_cost_data = costs[(costs['LOCATION_NAME'].isin(stores_list)) & (costs['FACILITY_NAME'].isin(facilities_list))]
