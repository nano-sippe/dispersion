.. refractive_index_database documentation master file, created by
   sphinx-quickstart on Wed Jun 10 21:37:18 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Refractive Index Database
=====================================================
The ``refractive_index_database`` Python package is provides a way of easily loading
and evaluating files containing refractive index (optical) data.

.. _ref-Setup:

Getting Started
===============

Python is required to install and use the ``refractive_index_database`` package. It
is recommended to use a package manager such as pip to install the package.
::

  > pip install refractive_index_database

now we need to tell the package where you are going to store the material data
files. To do this we run the script that comes with the package
::

  > setup_refractive_index_database

This script will ask you to type in the path to a folder where the database
file structure will be installed. Secondly, you will be asked to
name the database. Finally you will be asked if you would like to install
the available modules. See :ref:`ref-Modules` for more information.

now that the database has been setup, we can start using the package. For
examples and further documentation, see the related pages.

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :titlesonly:
	     
   material_database
   material_data
   spectral_data
   spectrum
   configuration
   modules
   test_autodoc


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
