import numpy as np
from refractive_index_database.spectrum import Spectrum
from refractive_index_database.spectral_data import SpectralData
from refractive_index_database.material_data import MaterialData
from refractive_index_database.material_database import MaterialDatabase
from refractive_index_database.io import Reader, Writer
from refractive_index_database.config import get_config
__version__ = "0.0.1"
__all__ = ["Spectrum", "SpectralData", "MaterialData", "MaterialDatabase"]

def get_permittivity(inputs):
    if not isinstance(inputs, dict):
        raise ValueError("this function requires a dicionary input")
    required_keys = {'path', 'name', 'EMOmega'}
    if not all(key in inputs for key in required_keys):
        raise ValueError("missing one of the following" +
                         "keys in input dict {}".format(required_keys))
    if not isinstance(inputs['name'], str):
        raise ValueError("input {} must be of type {}".format("name", str))
    if not isinstance(inputs['path'], str):
        raise ValueError("input {} must be of type {}".format("path", str))
    if not any(isinstance(inputs['EMOmega'], val) for val in
               {float, np.double, complex, np.cdouble}):
        raise ValueError("input {} must be" +
                         " of types {}".format("EMOmega",
                                               {float, np.double,
                                                complex, np.cdouble}))

    config = get_config()
    config['Path'] = inputs['path']
    mdb = MaterialDatabase(config=config)
    mat = mdb.get_material(inputs['name'])
    return mat.getPermittivity(inputs['EMOmega'],
                               spectrumType='angularFrequency',
                               unit='1/s')
