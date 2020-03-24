import pathlib
from setuptools import setup, find_packages


def parse_requirements(filename):
    '''
    Function to parse requirements.txt
    :param filename:
    :return:
    '''

    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


install_reqs = parse_requirements('requirements.txt')
reqs = install_reqs

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="cimren-kmedian-geo",
    version="0.0.1",
    description="k-Median modeling repo",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/emrahcimren/k-median-geo",
    author="cimren",
    author_email="cimren.1@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["kmedian_geo", "kmedian_geo/src"],
    include_package_data=True,
    install_requires=["setuptools", "Pathlib", "numpy", "ortools",
                      "pandas"] + reqs,
)
