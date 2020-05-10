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
        """
        Function to create parameters dictionary
        Args:
            parameter_df ():
            keys ():
            value ():

        Returns:

        """
        parameter_df = parameter_df.set_index(keys)
        return parameter_df[value].to_dict()

    def _create_store_facility_sets(self):
        """
        Store and facility set
        Returns:

        """
        print('creating store facility sets')
        self.store_set = self.stores['LOCATION_NAME'].unique()
        self.facility_set = self.facilities['FACILITY_NAME'].unique()

    def _create_store_facility_allocation_var_input(self):
        """
        Function to create store facility allocation sets
        Returns:

        """
        print('creating store facility allocation var')
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
        """
        Function to create facility selection set
        Returns:

        """
        print('creating facility selection var')
        self.facility_selection_var_input_set = self.facilities['FACILITY_NAME'].unique()

    def _create_facility_min_max_size(self):
        """
        Facility minimum and maximum number of elements
        Returns:

        """
        print('creating facility min max elements')
        self.facility_min_elements = self._create_parameter_dict(self.facilities, ['FACILITY_NAME'], 'MINIMUM_ELEMENTS')
        self.facility_max_elements = self._create_parameter_dict(self.facilities, ['FACILITY_NAME'], 'MAXIMUM_ELEMENTS')

    def _create_facility_maximum_demand(self):
        """
        Facility maximum demand
        Returns:

        """
        print('creating facility maximum demand')
        self.facility_maximum_demand = self._create_parameter_dict(self.facilities, ['FACILITY_NAME'], 'MAXIMUM_DEMAND')

    def _create_store_demand(self):
        """
        Store demand
        Returns:

        """
        print('creating store demand')
        self.store_demand = self._create_parameter_dict(self.stores, ['LOCATION_NAME'], 'DEMAND_UNITS')

    def _create_costs(self):
        """
        Costs between
        Returns:

        """
        print('creating costs')
        self.costs = self._create_parameter_dict(self.costs, ['LOCATION_NAME', 'FACILITY_NAME'], 'COST')
