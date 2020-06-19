File Format
===========

Files in the database can be in two different formats. Either as a text file
(.txt or .csv) or as a YAML file (.yml). An example of each format is
generated in the UserData module when installing the package.

Text File
---------
This is an example of the text file format,
::

  # This is a multiline meta-comment
  # which provides information not
  # in metadata
  # REFERENCES: Literature reference to the data
  # AUTHOR: The author of this data file
  # FULLNAME: Full name of the material
  # NAME: Short name of the material
  # COMMENTS: Any additional information goes here
  # SPECTRUMTYPE: wavelength
  # UNIT: nanometer
  # DATATYPE: tabulated nk
  #
  400.00000000	1.70000000	0.10000000
  500.00000000	1.60000000	0.05000000
  600.00000000	1.50000000	0.00000000
  700.00000000	1.40000000	0.00000000

- The optional metacomment comes at the beginning and can span multiple lines,
  each line must begin with #. The metacomment cannot contain :.
- The optional metadata is written in key:value pairs, one per line, beginning
  with a #. For a list of valid metadata categories, see MetaData_.
- Text files are restricted to datasets of tabulated data. For data defined
  via model parameters, use the YAML format.
- .txt files expects tab separated columns, .csv files should use comma
  separated columns.

YAML File
---------
This is an example of the yaml file format,
::

  # This is a multiline meta-comment
  # which provides information not
  # in metadata

  REFERENCES: Literature reference to the data
  COMMENTS: Any additional information goes here
  NAME: Short name of the material
  FULLNAME: Full name of the material
  AUTHOR: The author of this data file
  DATA:
    - DataType: model Sellmeier
      ValidRange: 0.35 2.
      SpectrumType: wavelength
      Unit: micrometer
      Yields: n
      Parameters: 0.    1.    0.05  2.    0.1  10.   25.
    - DataType: tabulated k
      ValidRange: 400. 600.
      SpectrumType: wavelength
      Unit: nm
      Data: |-
          4.e+02 1.e-01
          5.e+02 5.e-02
          6.e+02 0.e+00

- The optional metacomment comes at the beginning and can span multiple lines,
  each line must begin with #.
- The optional metadata is written in key:value pairs, one per line. For a list
  of valid metadata categories, see MetaData_.
- The DATA section can contain one or more data sets. Each data set after DATA:
  begins with a "-".
- Each type of data set can contain different types of metadata.


.. _MetaData:

MetaData
--------
Metadata is divided into two kinds, metadata for the file, and metadata for each
dataset.

**File Metadata**

REFERENCES
  Literature reference to the data

COMMENTS
  Any additional information

NAME
  Short name of the material

FULLNAME
  Full name of the material

AUTHOR
  The author of the data file

**Dataset Metadata**

DataType
  {tabulated_n, tabulated_k, tabulated_nk, tabulated_eps, model} For valid model
  names see :ref:`ref-SpectralData`

SpectrumType
  The type of spectrum. For more information see :ref:`ref-Spectrum`

Unit
  The physical unit of the spectrum. For more information see :ref:`ref-Spectrum`

ValidRange
  The spectral range that this data set covers

Data
  For tabulated data sets, the table of data.

Yields
  For model datasets, what values the model returns

Parameters
  For model datasets, the parameters or coefficients for the model
