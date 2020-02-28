import pytest
import numpy as np
from refractive_index_database.material_database import MaterialDatabase
from refractive_index_database.spectrum import Spectrum
#from refractive_index_database.config import get_config

spectrum = Spectrum(0.5,unit='um')

def test_mdb_init():
    mdb = MaterialDatabase()

def test_get_mat():
    mdb = MaterialDatabase()
    mat = mdb.get_material("Silver")
    nk = mat.get_nk_data(spectrum)
    assert np.isclose(np.real(nk),0.05)
    assert np.isclose(np.imag(nk),3.1308839999999996)
    
if __name__ == "__main__":
    pass
    
