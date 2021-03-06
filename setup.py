#!/usr/bin/env python
"""The setup script."""
import os
import re
import sys
from functools import reduce

from setuptools import find_packages
from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

requirements = ["requests", "matplotlib", "numpy", "astroquery",
                "scipy", "pandas", "glob2", "astropy", "dustmaps",
                "plotly", "ipython", "PyPDF2", "numdifftools", "lmfit",
                "ads", "emcee", "corner"]

test_requirements = []

# Thank you Andy Casey for this nice versioning method
major, minor1, minor2, release, serial = sys.version_info
readfile_kwargs = {"encoding": "utf-8"} if major >= 3 else {}


version_regex = re.compile('__version__ = "(.*?)"')
with open(
    reduce(os.path.join, [os.path.dirname(os.path.abspath(__file__)), "grblc", "__init__.py"]),
    **readfile_kwargs
) as fp:
    contents = fp.read()
    version = version_regex.findall(contents)[0]


setup(
    author="Sam Young",
    author_email="youngsam@sas.upenn.edu",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A Python package for GRB optical light curve studies.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="grblc",
    name="grblc",
    packages=find_packages(include=["grblc", "grblc.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/youngsm/grblc",
    version=version,
    zip_safe=False,
)
