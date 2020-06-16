import numpy as np

__version__ = "0.1.0"
__all__ = ["Spectrum", "Material", "Catalogue", "get_config",
           "Constant", "Interpolation", "Extrapolation",
           "Sellmeier", "Sellmeier2", "Polynomial",
           "RefractiveIndexInfo", "Cauchy", "Gases",
           "Herzberger", "Retro", "Exotic", "Drude",
           "DrudeLorentz", "rebuild_catalogue"]

from dispersion.spectrum import Spectrum
from dispersion.spectral_data import *
from dispersion.material import Material
from dispersion.catalogue import Catalogue, rebuild_catalogue
from dispersion.config import get_config
