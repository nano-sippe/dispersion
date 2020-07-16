import numpy as np
import sys
from dispersion.spectrum import Spectrum
from dispersion.spectral_data import *
from dispersion.io import Writer, Reader
from dispersion.material import Material
from dispersion.catalogue import Catalogue, rebuild_catalogue
from dispersion.config import get_config

__version__ = "0.1.0-beta.4"
__all__ = ["Spectrum", "Material", "Catalogue", "get_config",
           "Constant", "Interpolation", "Extrapolation",
           "Sellmeier", "Sellmeier2", "Polynomial",
           "RefractiveIndexInfo", "Cauchy", "Gases",
           "Herzberger", "Retro", "Exotic", "Drude",
           "DrudeLorentz", "rebuild_catalogue", "Writer", "Reader"]





#@staticmethod
# def _str_to_class(field):
#     """evaluates string as a class.
#
#     tries to evaluate the given string as a class from the spectral_data
#     module.
#
#     Parameters
#     ----------
#     field: str
#         name to convert to class
#
#     Raises
#     ------
#     NameError
#         the given field is not an attribute
#     TypeError
#         the given field is an attribute but not a class
#     """
#     try:
#         identifier = getattr(sys.modules[__name__], field)
#     except AttributeError:
#         raise NameError("%s doesn't exist." % field)
#     if isinstance(identifier, type):
#         return identifier
#     raise TypeError("%s is not a class." % field)
