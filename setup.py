# -*- coding: utf-8 -*-
"""
This module contains the tool of uwosh.pfg.d2c
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1'

long_description = (
    read('uwosh', 'pfg', 'd2c', 'README.txt') + '\n\n' +
    read('CHANGES.txt')
    + '\n\n' +
    'Contributors\n'
    '************\n'
    + '\n\n' +
    read('CONTRIBUTORS.txt')
    + '\n' 
    )

tests_require=['zope.testing']

setup(name='uwosh.pfg.d2c',
      version=version,
      description="A PloneFormGen adapter that will save the data from a form to an actual content type. This way you can still use permissions, workflows, etc on the form data.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='ploneformgen plone forms adapter uwosh',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uwosh', 'uwosh.pfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.PloneFormGen',
        'archetypes.schemaextender'
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'uwosh.pfg.d2c.tests',
      entry_points="""
      # -*- entry_points -*- 
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
