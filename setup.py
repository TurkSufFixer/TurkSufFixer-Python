# -*- coding: UTF-8 -*-
from setuptools import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='turksuffixer',
    version='0.2.3',
    description='Suffix generator for Turkish language',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/TurkSufFixer/TurkSufFixer-Python',
    author='Talha Çolakoğlu',
    author_email='talhacolakoglu@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    keywords='turkish suffix',
    packages=['turksuffixer'],
    package_data={'data': ['sozluk/*']},
)
