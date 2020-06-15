import numpy as np
from refractive_index_database.spectrum import Spectrum
from refractive_index_database.spectral_data import SpectralData
from refractive_index_database.material_data import MaterialData
from refractive_index_database.material_database import MaterialDatabase
from refractive_index_database.io import Reader
from refractive_index_database.config import get_config
__version__ = "0.0.1"
__all__ = ["Spectrum", "SpectralData", "MaterialData", "MaterialDatabase"]
