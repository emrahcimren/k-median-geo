'''
Creates the main logger as well as the handlers to capture the logs
'''

import logging
import pathlib


def set_logger(run_id, logging_file_path, file_name):
    '''
    File to create loggers
    :param run_id: Unique ID for a run
    :param logging_file_path: Where logger main path located
    :param file_name: Name of the logger file
    :return: Log files
    '''

    logger = logging.getLogger()

    base_path = pathlib.Path(logging_file_path)
    pathlib.Path(base_path / 'debug').mkdir(parents=True, exist_ok=True)
    pathlib.Path(base_path / 'warning').mkdir(parents=True, exist_ok=True)

    debug_path = base_path / 'debug'
    warning_path = base_path / 'warning'

    # create directory structure if needed
    create_directory_structure(debug_path)
    create_directory_structure(warning_path)

    final_path = debug_path / ('__' + file_name + '___' + run_id + '.log')
    debug_fhandler = logging.FileHandler(filename=final_path, mode='w')

    final_path = warning_path / ('__' + file_name + '___' + run_id + '.log')
    warning_fhandler = logging.FileHandler(filename=final_path, mode='w')

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s')

    debug_fhandler.setFormatter(formatter)
    warning_fhandler.setFormatter(formatter)

    logger.addHandler(debug_fhandler)
    logger.addHandler(warning_fhandler)

    logger.setLevel(logging.DEBUG)

    debug_fhandler.setLevel(logging.DEBUG)
    warning_fhandler.setLevel(logging.WARNING)

    return debug_path / ('__' + file_name + '___' + run_id)


def create_directory_structure(directory_path):
    """
    Creates directory structure, include upstream parents, if they do not exist.

    director_path (Path):
        The full folder path structure
    """
    if not directory_path.exists():
        directory_path.mkdir(parents=True)
