import pytest
import numpy as np
import os
from refractive_index_database.material_data import MaterialData
from refractive_index_database.spectrum import Spectrum
from refractive_index_database.config import get_config

spectrum = Spectrum(0.5,unit='um')

def test_md_init():
    md = MaterialData(fixed_n=1.0)
    n = md.get_nk_data(spectrum)
    assert np.isclose(np.real(n), 1.0)
    assert np.isclose(np.imag(n), 0.0)

def test_from_yml_file():
    config = get_config()
    relpath = os.path.join('RefractiveIndexInfo',
                           'data','main','Ag',
                           'Hagemann.yml')
    filepath = os.path.join(config['Path'],relpath)
    md = MaterialData(file_path=filepath,
                      spectrum_type='wavelength',
                      unit='micrometer')
    n = md.get_nk_data(spectrum)
    assert np.isclose(np.real(n), 0.23805806451612901)
    assert np.isclose(np.imag(n), 3.126040322580645)    

def test_from_txt_file():
    config = get_config()
    relpath = os.path.join('UserData','AlSb.txt')
    filepath = os.path.join(config['Path'],relpath)
    md = MaterialData(file_path=filepath,
                      spectrum_type='wavelength',
                      unit='micrometer')
    n = md.get_nk_data(spectrum)
    assert np.isclose(np.real(n), 4.574074754901961)
    assert np.isclose(np.imag(n), 0.4318627450980393)    
    
    
def test_from_model():
    wp = 8.55 # eV
    loss = 18.4e-3 #eV
    model_kw = {'name':'Drude','parameters':[wp,loss],
                'valid_range':[0.0,np.inf],
                'spectrum_type':'energy','unit':'ev'}
    md = MaterialData(model_kw=model_kw)
    n = md.get_nk_data(spectrum)

    assert np.isclose(np.real(n), 0.013366748652710245)
    assert np.isclose(np.imag(n), 3.2997524521729824)
    
if __name__ == "__main__":
    pass

    
    
