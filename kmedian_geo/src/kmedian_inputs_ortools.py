class ModelInputs:

    def __init__(self, stores, facilities, costs):

        self.stores = stores
        self.facilities = facilities
        self.costs = costs

        self._create_store_facility_sets()
        self._create_store_facility_allocation_var_input()
        self._create_facility_selection_var_input()
        self._create_facility_min_max_size()
        self._create_facility_maximum_demand()
        self._create_store_demand()
        self._create_costs()

    @staticmethod
    def _create_parameter_dict(parameter_df, keys, value):
        '''
        Function to create parameters dictionary
        :param parameter_df:
        :param keys:
        :param value:
        :return:
        '''
        parameter_df = parameter_df.set_index(keys)
        return parameter_df[value].to_dict()

    def _create_store_facility_sets(self):
        '''
        Store and facility set
        :return:
        '''
        self.store_set = self.stores['LOCATION_NAME'].unique()
        self.facility_set = self.facilities['FACILITY_NAME'].unique()

    def _create_store_facility_allocation_var_input(self):
        '''
        Function to create store facility allocation sets
        :return:
        '''
        facilities_input = self.facilities.copy()
        facilities_input['key'] = 0
        facilities_input = facilities_input[['FACILITY_NAME', 'key']]

        stores_input = self.stores.copy()
        stores_input['key'] = 0
        stores_input = stores_input[['LOCATION_NAME', 'key']]

        self.store_facility_allocation_var_input = facilities_input.merge(stores_input, on=['key'])
        self.store_facility_allocation_var_input.drop(['key'], 1, inplace=True)
        self.store_facility_allocation_var_input = self.store_facility_allocation_var_input[
            ['LOCATION_NAME', 'FACILITY_NAME']]

        self.store_facility_allocation_var_input_set = self.store_facility_allocation_var_input.apply(tuple,
                                                                                                      axis=1).tolist()

    def _create_facility_selection_var_input(self):
        '''
        Function to create facility selection set
        :return:
        '''
        self.facility_selection_var_input_set = self.facilities['FACILITY_NAME'].unique()

    def _create_facility_min_max_size(self):
        '''
        Facility minimum and maximum number of elements
        :return:
        '''
        self.facility_min_elements = self._create_parameter_dict(self.facilities, ['FACILITY_NAME'], 'MINIMUM_ELEMENTS')
        self.facility_max_elements = self._create_parameter_dict(self.facilities, ['FACILITY_NAME'], 'MAXIMUM_ELEMENTS')

    def _create_facility_maximum_demand(self):
        '''
        Facility maximum demand
        :return:
        '''
        self.facility_maximum_demand = self._create_parameter_dict(self.facilities, ['FACILITY_NAME'], 'MAXIMUM_DEMAND')

    def _create_store_demand(self):
        '''
        Store demand
        :return:
        '''
        self.store_demand = self._create_parameter_dict(self.stores, ['LOCATION_NAME'], 'DEMAND_UNITS')

    def _create_costs(self):
        '''
        Costs between
        :return:
        '''
        self.costs = self._create_parameter_dict(self.costs, ['LOCATION_NAME', 'FACILITY_NAME'], 'COST')
