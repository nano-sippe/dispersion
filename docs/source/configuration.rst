Configuration
=============

Some of the features of the package are configurable. These can be changed in
configuration file. In order to use the ``Catalogue`` class, a valid configuration
file (config.yaml) needs to be used. when setting up the package (see :ref:`ref-Setup` ) a new configuration
file with default values will be created.

Location
--------
The config file can exist in two different locations. The first location is a user specific
directory, for linux systems this is,

::

   ~/.config/refractive_index_database

whereas on windows systems this is,

::

   %LOCALAPPDATA%\refractive_index_database

this is also the default directory used when creating a new configuration if no config file
exists. If no config file is found in this location, the package looks in the package directory.

Values
------
**Path**
    **Type**: *str*

    The path to the root of the database file system

**File**
    **Type**: *str*

    Name of the catalogue file (will be located in directory defined by Path)

**Interactive**
    **Type**: *bool*

    Set to true for interactive editing of the database in IPython (requires ``qgrid``)

**Plotting**
    **Type**: *bool*

    Set to true for plotting of material data (requires ``matplotlib``)

**Modules**
    **Type**: *dict*

    modules to be included in the database

**ReferenceSpectrum**
    **Type**: *dict*

    use Value, SpectrumType and Unit to define the spectral value at which the
    reference spectrum will be calculated when building the database
