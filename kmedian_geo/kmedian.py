
from kmedian_geo.src import kmedian_inputs as kmi


def run_kmedian_model(stores,
                      facilities,
                      costs,
                      solver='or tools'):
    '''
    Function to run kmedian model
    :param stores:
    :param facilities:
    :param costs:
    :param solver:
    :return:
    '''

    mi = kmi.ModelInputs(stores,
                         facilities,
                         costs)

    if solver=='or tools':

        from kmedian_geo.src import kmedian_model_ortools as ort

