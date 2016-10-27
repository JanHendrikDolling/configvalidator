# -*- coding: utf-8 -*-
"""
:copyright: (c) 2015 by Jan-Hendrik Dolling.
:license: Apache 2.0, see LICENSE for more details.
"""
import sys
import re
from setuptools import setup, find_packages

version = ''
with open('configvalidator/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst') as fh:
    long_description = fh.read()

test_requirements = ["pep8", "nose", "mock", "pyOpenSSL", "coverage"]
if sys.version_info[0] == 2 and sys.version_info[1] == 6:
    test_requirements.append("unittest2")
    test_requirements.append("ordereddict")

setup(
    name = "ConfigValidator",
    version = version,
    description='python module to Validate ini File user input',
    long_description=long_description,
    author='Jan-Hendrik Dolling',
    url='https://github.com/JanHendrikDolling/configvalidator',
    download_url = 'https://github.com/JanHendrikDolling/configvalidator/archive/master.zip',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=['six'],
    tests_require = test_requirements,
    classifiers=[
         'Development Status :: 4 - Beta',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Programming Language :: Python :: 3',
         'Programming Language :: Python :: 3.3',
         'Programming Language :: Python :: 3.4',
         'Programming Language :: Python :: 3.5',
     ],
)
