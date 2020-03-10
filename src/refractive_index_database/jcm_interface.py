from numpy import *
from refractive_index_database.config import get_config
from refractive_index_database.material_database import MaterialDatabase

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
               {float, complex}):
        raise ValueError("input {} must be" +
                         " of types {}".format("EMOmega",
                                               {float, complex}))

    config = get_config()
    config['Path'] = inputs['path']
    mdb = MaterialDatabase(config=config)
    mat = mdb.get_material(inputs['name'])
    return eye(3,3)*mat.get_permittivity(inputs['EMOmega'],
                               spectrum_type='angularfrequency',
                               unit='1/s')
