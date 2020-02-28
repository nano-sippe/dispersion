import pytest
import numpy as np
from refractive_index_database.spectrum import Spectrum

def test_scalar_init():
    spectrum = Spectrum(1.3)

def test_list_init():
    spectrum = Spectrum([0.5, 1.0])

def test_standardise():
    spectrum = Spectrum([0.5, 1.0])
    assert spectrum.standard_rep[0] == 0.5
    assert spectrum.standard_rep[1] == 1.0

def test_from_wavelength():
    spectrum1 = Spectrum([500, 800],
                         spectrum_type = 'wavelength',
                         unit='nanometer')    
    assert np.isclose(spectrum1.standard_rep[0], 5.e-7)
    assert np.isclose(spectrum1.standard_rep[1], 8.e-7)

    spectrum2 = Spectrum([0.5, 0.8],
                         spectrum_type = 'wavelength',
                         unit='micrometre')    
    assert np.isclose(spectrum1.standard_rep[0], 5.e-7)
    assert np.isclose(spectrum1.standard_rep[1], 8.e-7)
    

def test_from_energy():
    spectrum = Spectrum([1.0, 2.0],
                        spectrum_type='energy',
                        unit='ev')    
    assert np.isclose(spectrum.standard_rep[0], 1.23984198e-06)
    assert np.isclose(spectrum.standard_rep[1], 6.19920992e-07)

def test_from_frequency():
    spectrum = Spectrum([1e15, 1e16],
                        spectrum_type='frequency',
                        unit='hz')    
    assert np.isclose(spectrum.standard_rep[0], 2.99792458e-07)
    assert np.isclose(spectrum.standard_rep[1], 2.99792458e-08)

def test_from_ang_frequency():
    spectrum = Spectrum([2e15, 3e16],
                        spectrum_type='angularfrequency',
                        unit='1/s')    
    assert np.isclose(spectrum.standard_rep[0], 9.41825784e-07)
    assert np.isclose(spectrum.standard_rep[1], 6.27883856e-08)

def test_from_wavenumber():
    spectrum = Spectrum([12500., 25000.],
                        spectrum_type='wavenumber',
                        unit='1/cm')    
    assert np.isclose(spectrum.standard_rep[0], 5.02654825e-06)
    assert np.isclose(spectrum.standard_rep[1], 2.51327412e-06)



def test_from_energy():
    spectrum = Spectrum([500, 800],
                         spectrum_type = 'wavelength',
                         unit='nanometer')

    vals = spectrum.convert_to('energy','ev')

def test_to_frequency():
    spectrum = Spectrum([500, 800],
                         spectrum_type = 'wavelength',
                         unit='nanometer')

    vals = spectrum.convert_to('frequency','hz')

def test_to_angfrequency():
    spectrum = Spectrum([500, 800],
                         spectrum_type = 'wavelength',
                         unit='nanometer')

    vals = spectrum.convert_to('angularfrequency','1/s')

def test_to_wavenumber():
    spectrum = Spectrum([500, 800],
                         spectrum_type = 'wavelength',
                         unit='nanometer')

    vals = spectrum.convert_to('wavenumber','1/cm')

def test_contains():
    spectrum1 = Spectrum([400., 800.],
                         spectrum_type = 'wavelength',
                         unit='nanometer')

    spectrum2 = Spectrum([500., 700.],
                         spectrum_type = 'wavelength',
                         unit='nanometer')

    assert spectrum1.contains(spectrum2)
