# -*- coding: utf-8 -*-
"""
This module contains the tool of uwosh.pfg.d2c
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.5.0.dev0'

long_description = (
    read('README.rst') + '\n\n' +
    read('CHANGES.txt')
    + '\n\n' +
    'Contributors\n'
    '============\n'
    + '\n\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

tests_require = [
    'Products.PloneTestCase',
    'plone.app.testing',
    'plone.testing',
]

setup(name='uwosh.pfg.d2c',
      version=version,
      description="A PloneFormGen adapter that will save the data from a form "
                  "to an actual content type. This way you can still use "
                  "permissions, workflows, etc on the form data.",
      long_description=long_description,
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='ploneformgen plone forms adapter uwosh',
      author='Nathan Van Gheem',
      author_email='vangheem@gmail.com',
      url='https://github.com/collective/uwosh.pfg.d2c/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['uwosh', 'uwosh.pfg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.PloneFormGen',
        'archetypes.schemaextender',
        'Products.TALESField',
      ],
      tests_require=tests_require,
      test_suite='uwosh.pfg.d2c.tests',
      extras_require=dict(
         tests=tests_require,
         docs=['Sphinx',
            'z3c.recipe.sphinxdoc',
            'repoze.sphinx.autointerface',
            'collective.sphinx.includedoc >= 0.2'
         ],
      ),
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
