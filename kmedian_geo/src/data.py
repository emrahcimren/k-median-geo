import pandas as pd
import os
current_dir, this_filename = os.path.split(__file__)

stores = pd.read_pickle(os.path.join(current_dir, 'kmedian_geo/data/stores.pkl'))
facilities = pd.read_pickle(os.path.join(current_dir, 'kmedian_geo/data/facilities.pkl'))
costs = pd.read_pickle(os.path.join(current_dir, 'kmedian_geo/data/costs.pkl'))
