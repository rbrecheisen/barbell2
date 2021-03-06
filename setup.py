#!/usr/bin/env python

import os

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['pytest', 'pydicom', 'pandas', 'numpy', 'SimpleITK', 'h5py', 'tensorflow', 'cmd2']

setup_requirements = []

test_requirements = []

setup(
    author="Ralph Brecheisen",
    author_email='ralph.brecheisen@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Collection of Python libraries and tools",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='barbell2',
    name='barbell2',
    packages=find_packages(include=['barbell2', 'barbell2.*']),
    setup_requires=setup_requirements,
    entry_points={
        'console_scripts': [
            'dicomexplorer=barbell2.dicomexplorer.dicomexplorer:main',
        ],
    },
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rbrecheisen/barbell2',
    version=os.environ['VERSION'],
    zip_safe=False,
)
