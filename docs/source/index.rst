.. dispersion documentation master file, created by
   sphinx-quickstart on Wed Jun 10 21:37:18 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dispersion
==========

    *In optics, the phenomenon that the refractive index depends upon the*
    *frequency is called the phenomenon of dispersion, because it is the basis*
    *of the fact that light is “dispersed” by a prism into a spectrum.*

    *Feynman Lectures in physics* [1_]

The ``dispersion`` Python package provides a way of loading and evaluating files
containing the dispersion of the refractive index of materials.

.. _1: https://www.feynmanlectures.caltech.edu/I_31.html

.. _ref-Setup:

Getting Started
---------------

Python is required to install and use the ``dispersion`` package. It
is recommended to use a package manager such as pip to install the package.
::

  > pip install dispersion

now we need to tell the package where you are going to store the material data
files. To do this we run the script that comes with the package
::

  > setup_dispersion

This script will ask you to type in the path to a folder where the database
file structure will be installed. Secondly, you will be asked to
name the database. Finally you will be asked if you would like to install
the available modules. See :ref:`ref-Modules` for more information.

Now that the database has been setup, we can start using the package. For
examples and further documentation, see the related pages.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :titlesonly:

   catalogue
   material
   spectral_data
   spectrum
   configuration
   modules
   file_format


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
