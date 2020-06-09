from numpy import *
import sys
import os

def get_permittivity(inputs):
    print(inputs)

    if not isinstance(inputs, dict):
        raise ValueError("this function requires a dicionary input")
    required_keys = {'path', 'name', 'EMOmega'}
    for required_key in required_keys:
        if required_key not in inputs:
            raise ValueError("missing {} in input dict".format(required_key))
    if not isinstance(inputs['name'], str):
        raise ValueError("input {} must be of type {}".format("name", str))
    if not isinstance(inputs['path'], str):
        raise ValueError("input {} must be of type {}".format("path", str))
    correct_type = False
    for val in {float, complex}:
        if isinstance(inputs['EMOmega'], val):
            correct_type = True

    if not correct_type:
        raise ValueError("input EMOmega must be" +
                         " of types {}".format({float, complex}))

    from refractive_index_database.config import get_config
    from refractive_index_database.material_database import MaterialDatabase

    config = get_config()
    config['Path'] = inputs['path']
    mdb = MaterialDatabase(config=config)
    mat = mdb.get_material(inputs['name'])
    omega = real(inputs['EMOmega']).reshape(1,)
    complex_eps = mat.get_permittivity(omega,
                               spectrum_type='angularfrequency',
                               unit='1/s')
    return eye(3,3)*complex_eps
