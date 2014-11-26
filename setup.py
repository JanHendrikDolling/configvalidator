# -*- coding: utf-8 -*-
"""
Created on 24.11.2014

@license: http://www.apache.org/licenses/LICENSE-2.0
@author: Jan-Hendrik Dolling
"""
import sys
from setuptools import setup

with open('README.md') as fh:
    long_description = fh.read()

if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    test_requirements = ["pep8", "pytest", "unittest2", "mock"]
else:
    test_requirements = ["pep8", "pytest"]
    if sys.version_info[0] < 3 or sys.version_info[1] < 3:
        test_requirements.append("mock")

setup(
    name = "ConfigValidator",
    version = "0.1.1",
    description='python module to Validate ini File user input',
    long_description=long_description,
    author='Jan-Hendrik Dolling',
    url='https://github.com/JanHendrikDolling/configvalidator',
    download_url = 'https://github.com/JanHendrikDolling/configvalidator/archive/master.zip',
    license='Apache License 2.0',
    packages=['configvalidator'],
    install_requires=['six'],
    tests_require = test_requirements,
    classifiers=[
         'Development Status :: 4 - Beta',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3.2',
         'Programming Language :: Python :: 3.3',
         'Programming Language :: Python :: 3.4',
     ],
)
