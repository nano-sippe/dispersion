from numpy import *
import sys
import os

def get_permittivity(inputs):
    if not isinstance(inputs, dict):
        raise ValueError("this function requires a dicionary input")
    required_keys = {'Path', 'Name', 'EMOmega'}
    for required_key in required_keys:
        if required_key not in inputs:
            raise ValueError("missing {} in input dict".format(required_key))
    if not isinstance(inputs['Name'], str):
        raise ValueError("input {} must be of type {}".format("Name", str))
    if not isinstance(inputs['Path'], str):
        raise ValueError("input {} must be of type {}".format("Path", str))
    correct_type = False
    inputs['EMOmega'] = inputs['EMOmega'].reshape(1,)
    for val in {float, complex}:
        if isinstance(inputs['EMOmega'][0], val):
            correct_type = True

    if not correct_type:
        raise ValueError("input EMOmega must be" +
                         " of types {}".format({float, complex}))

    from refractive_index_database.config import get_config
    from refractive_index_database.material_database import MaterialDatabase

    config = get_config()
    config['Path'], config['File'] = os.path.split(inputs['Path'])
    
    mdb = MaterialDatabase(config=config)
    mat = mdb.get_material(inputs['Name'])
    omega = real(inputs['EMOmega'])
    complex_eps = mat.get_permittivity(omega,
                               spectrum_type='angularfrequency',
                               unit='1/s')
    return_val = eye(3)*complex_eps
    return return_val
