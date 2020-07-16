Change Log
==========

- 0.1.0.beta3

  - automatic github integration with pypi database.

- 0.1.0.beta2

  - numerous typos fixed

  - enabled plotting using the matplotlib package

  - when taking the inverse of a spectrum, the order of the data is now reversed

  - added qgrid installation information to documentation

  - added rounding to 9 decimal places when converting to energy

  - added the Tauc Lorentz Model for permittivity

  - added the EffectiveMedium class for effective mediums of multiple materials

  - MaxwellGarnett and Bruggeman provide the respective effective media

  - updated the DrudeLorentz model definition to include oscillator strength

  - when converting spectrum_type and unit using inplace=True, the spectrum_type
    and unit will not be converted as well as the values
