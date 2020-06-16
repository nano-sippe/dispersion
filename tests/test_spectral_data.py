"""ToDo add unit tests for all models"""
import pytest
import numpy as np
from dispersion import Constant, Interpolation, Sellmeier, Drude
from dispersion import Spectrum

def test_constant_init():
    spec_data = Constant(1.2)
    spectrum = Spectrum([500e-9])
    assert np.isclose(spec_data.evaluate(spectrum),1.2)

def test_interpolation():
    data = np.array([[500,1.2],
                     [800,1.4]])
    spec_data = Interpolation(data,unit='nanometer')
    spectrum = Spectrum(500e-9)
    assert np.isclose(spec_data.evaluate(spectrum),1.2)
    spectrum = Spectrum(800e-9)
    assert np.isclose(spec_data.evaluate(spectrum),1.4)

def test_sellmeier():
    model_parameters = [0, 0.6961663, 0.0684043, 0.4079426,
                      0.1162414, 0.8974794, 9.896161]
    spec_data = Sellmeier(model_parameters,valid_range=[0.21,6.7],
                          unit='um')
    spectrum = Spectrum(0.5876e-6)
    assert np.isclose(spec_data.evaluate(spectrum),1.4585,atol=1e-3)

def test_drude():
    model_parameters = [8.55, 18.4e-3]
    spec_data = Drude(model_parameters,valid_range=[0.0,np.inf],
                          unit='ev',spectrum_type='energy')
    spectrum = Spectrum(0.5876e-6)
    spec_data.evaluate(spectrum)
    #assert np.isclose(spec_data.evaluate(spectrum),1.4585,atol=1e-3)
