"""spectral_data implements the abstract base class SpectralData which
defines a material parameter which has a spectral dependence (e.g.
refractive index, permittivity). Each of the subclasses must implement
the evaluate method which returns the material parameter for a given
Spectrum object.

SpectralData has the following subclasses:
  Constant: for values that are independent of the spectrum
  Interplation: for tabulated data values
  Model: for values generated from a particular model

Model is an abstract base class. Each subclass must implement the methods
input_output as well as evaluate.

Model has the following subclasses:
  [Sellmeier, Sellmeier2, Polynomial, RefractiveIndexInfo,
   Cauchy, Gases, Herzberger, Retro, Exotic, Drude, DrudeLorentz]
"""

import numpy as np
from scipy.interpolate import interp1d, splrep, splev
from refractive_index_database.spectrum import Spectrum


class SpectralData(object):
    '''
    Base class for defining a quantity (e.g. refactive index)
    which is defined over a given spectrum (see class Spectrum.

    '''

    def __init__(self, valid_range,
                 spectrum_type='wavelength',
                 unit='nm'):
        self.spectrum_type = spectrum_type
        self.unit = unit
        self.valid_range = Spectrum(valid_range,
                                    spectrum_type=spectrum_type,
                                    unit=unit)

    def suggest_spectrum(self):
        """for plotting the spectral data we take a geometrically
        spaced set of values"""
        lower_bound = np.min(self.valid_range.values)
        upper_bound = np.max(self.valid_range.values)
        suggest = np.geomspace(lower_bound, upper_bound, num=1000)
        return Spectrum(suggest,
                        spectrum_type=self.spectrum_type,
                        unit=self.unit)

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        raise NotImplementedError("This method should be overridden by"+
                                  " a subclass")

class Constant(SpectralData):
    """for spectral data values that are independent of the spectrum"""

    def __init__(self, constant, valid_range=(0, np.inf),
                 spectrum_type='wavelength',
                 unit='m'):
        super(Constant, self).__init__(valid_range,
                                       spectrum_type=spectrum_type,
                                       unit=unit)
        self.constant = constant

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        self.valid_range.contains(spectrum)
        if isinstance(spectrum.values, (list, tuple, np.ndarray)):
            return self.constant * np.ones(len(spectrum.values))
        return self.constant

class Extrapolation(SpectralData):
    """
    for extending spectral data outside of the valid range.
    Use with caution
    """
    def __init__(self, spectral_data, extended_spectrum,
                 spline_order=2):
        self.base_spectral_data = spectral_data
        self.spline_order = spline_order
        extrap_spectrum = self.get_extrap_spectrum(extended_spectrum)
        min_range = np.min(extrap_spectrum.values)
        max_range = np.max(extrap_spectrum.values)
        spectrum_type = self.base_spectral_data.spectrum_type
        unit = self.base_spectral_data.unit
        super(Extrapolation, self).__init__((min_range, max_range),
                                            spectrum_type=spectrum_type,
                                            unit=unit)
        self.extrapolate_data()

    def get_extrap_spectrum(self,extended_spectrum):
        """
        takes a Spectrum object with one or two values possibly lying outside
        the base spectral range. Raises an error if the values do not lie
        outside the base spectral range. returns a new length two spectrum
        that gives the lower and upper bound for an extrapolation
        """
        base_spectrum = self.base_spectral_data.valid_range
        extended_spectrum.convert_to(spectrum_type= base_spectrum.spectrum_type,
                                     unit= base_spectrum.unit,
                                     in_place= True)
        new_range = np.array(base_spectrum.values)
        if isinstance(extended_spectrum.values, (list, tuple, np.ndarray)):
            # extrapolation both upper and lower
            extrap_values = extended_spectrum.values
            if extrap_values.size > 2:
                raise ValueError("extrapolation spectrum may contain at most" +
                                 "2 values not {}".format(extrap_values.size))
            for extrap_val in extrap_values:
                new_range = self.validate_extrap_val(extrap_val,new_range)
        else:
            # upper or lower
            extrap_val = extended_spectrum.values
            new_range = self.validate_extrap_val(extrap_val,new_range)

        return Spectrum(new_range,
                        spectrum_type= base_spectrum.spectrum_type,
                        unit= base_spectrum.unit)

    def validate_extrap_val(self,extrap_val,base_range):
        """
        checks if extrap_val lies outside base_range and replaces the relevant
        value in base_range with extrap_val.
        """
        if extrap_val < base_range[0]:
            base_range[0] = extrap_val
        elif extrap_val > base_range[1]:
            base_range[1] = extrap_val
        else:
            raise ValueError("extrapolation value of " +
                             "{} ".format(extrap_val) +
                             "lies inside the defined range " +
                             "{}".format(base_range) +
                             " therefore extrapolation is not necessary")
        return base_range


    def extrapolate_data(self):
        """makes a spline base on the base data for future lookup"""
        spectrum = self.base_spectral_data.suggest_spectrum()
        evaluation = self.base_spectral_data.evaluate(spectrum)
        self.extrapolation = splrep(spectrum.values, evaluation,
                                    k=self.spline_order)

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the fiven spectrum"""
        try:
            self.base_spectral_data.valid_range.contains(spectrum)
            return self.base_spectral_data.evaluate(spectrum)
        except ValueError as e:
            spectrum.convert_to(self.spectrum_type, self.unit, in_place=True)
            self.valid_range.contains(spectrum)
            return splev(spectrum.values,self.extrapolation)


class Interpolation(SpectralData):
    """for spectral data values that are from tabulated data"""

    def __init__(self, data, spectrum_type='wavelength',
                 unit='m', interp_order=1):
        self.data = data
        self.interp_order = interp_order
        min_range = np.min(data[:, 0])
        max_range = np.max(data[:, 0])
        super(Interpolation, self).__init__((min_range, max_range),
                                            spectrum_type=spectrum_type,
                                            unit=unit)
        self.interpolate_data()

    def interpolate_data(self):
        """interpolates the data for future lookup"""
        self.interpolation = interp1d(self.data[:, 0], self.data[:, 1],
                                      kind=self.interp_order)

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the fiven spectrum"""

        self.valid_range.contains(spectrum)
        values = spectrum.convert_to(self.spectrum_type, self.unit)
        return self.interpolation(values)

class Model(SpectralData):
    """for spectral data values depending on model parameters"""

    def __init__(self, model_parameters, valid_range, spectrum_type='wavelength',
                 unit='m'):
        self.model_parameters = model_parameters
        super(Model, self).__init__(valid_range,
                                    spectrum_type=spectrum_type,
                                    unit=unit)
        self.required_spectrum_type = None # set in input_output
        self.required_unit = None # set in input_output
        self.input_output()
        tmp_spectrum = Spectrum(1.0,
                                spectrum_type=self.spectrum_type,
                                unit=self.unit)

        if not tmp_spectrum.spectrum_type == self.required_spectrum_type:
            raise ValueError("spectrum_type for model " +
                             "<{}> must".format(type(self).__name__) +
                             " be {}".format(self.required_spectrum_type))

        if not tmp_spectrum.unit == self.required_unit:
            raise ValueError("unit for model " +
                             "<{}> must".format(type(self).__name__) +
                             "be {}".format(self.required_unit))

    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        raise NotImplementedError("this abstract method needs to be"+
                                  "overridden by a subclass")

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        raise NotImplementedError("this abstract method needs to be"+
                                  "overridden by a subclass")

    def preprocess(self, spectrum):
        """
        check range of spectrum, convert to correct sType and unit and return
        an object with the same tensor order (scalar|vector) with values set
        to 1.0
        """
        self.valid_range.contains(spectrum)
        new_spectrum = spectrum.convert_to(self.spectrum_type,
                                           self.unit)
        if isinstance(spectrum, (list, tuple, np.ndarray)):
            ones = np.ones(new_spectrum.shape)
        else:
            ones = 1.0
        return ones, new_spectrum

class Sellmeier(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'


    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlsq = np.power(wavelengths, 2)
        for iterc in range(len(self.model_parameters[1::2])):
            cupper = self.model_parameters[iterc*2+1]
            clower = self.model_parameters[iterc*2+2]
            rhs += cupper*wvlsq/(wvlsq-clower**2)
        ref_index = np.sqrt(rhs+1.0)
        return ref_index

class Sellmeier2(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlsq = np.power(wavelengths, 2)
        for iterc in range(len(self.model_parameters[1::2])):
            cupper = self.model_parameters[iterc*2+1]
            clower = self.model_parameters[iterc*2+2]
            rhs += cupper*wvlsq/(wvlsq-clower)
        ref_index = np.sqrt(rhs+1.0)
        return ref_index

class Polynomial(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones

        for iterc in range(len(self.model_parameters[1::2])):
            c_multi = self.model_parameters[iterc*2+1]
            c_power = self.model_parameters[iterc*2+2]
            rhs += c_multi*np.power(wavelengths, c_power)
        ref_index = np.sqrt(rhs)
        return ref_index

class RefractiveIndexInfo(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlsq = np.power(wavelengths, 2)
        for iterc in range(len(self.model_parameters[1:8:4])):
            c_multi_upper = self.model_parameters[iterc*4+1]
            c_power_upper = self.model_parameters[iterc*4+2]
            c_multi_lower = self.model_parameters[iterc*4+3]
            c_power_lower = self.model_parameters[iterc*4+4]
            rhs += (c_multi_upper*np.power(wavelengths, c_power_upper)/
                    (wvlsq-np.power(c_multi_lower, c_power_lower)))
        for iterc in range(len(self.model_parameters[9::2])):
            c_multi = self.model_parameters[iterc*2+9]
            c_power = self.model_parameters[iterc*2+10]
            rhs += c_multi*np.power(wavelengths, c_power)
        ref_index = np.sqrt(rhs)
        return ref_index



class Cauchy(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        for iterc in range(len(self.model_parameters[1::2])):
            c_multi = self.model_parameters[iterc*2+1]
            c_power = self.model_parameters[iterc*2+2]
            rhs += c_multi*np.power(wavelengths, c_power)
        ref_index = rhs
        return ref_index

class Gases(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlinvsq = np.power(wavelengths, -2)
        for iterc in range(len(self.model_parameters[1::2])):
            cupper = self.model_parameters[iterc*2+1]
            clower = self.model_parameters[iterc*2+2]
            rhs += cupper/(clower-wvlinvsq)
        ref_index = rhs+1.0
        return ref_index

class Herzberger(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlsq = np.power(wavelengths, 2)
        rhs += self.model_parameters[1]*np.power(wvlsq-0.028, -1)
        rhs += self.model_parameters[2]*np.power(wvlsq-0.028, -2)
        rhs += self.model_parameters[3]*wvlsq
        rhs += self.model_parameters[4]*np.power(wavelengths, 4)
        rhs += self.model_parameters[5]*np.power(wavelengths, 6)

        ref_index = rhs
        return ref_index

class Retro(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlsq = np.power(wavelengths, 2)
        rhs += self.model_parameters[1]*wvlsq/(wvlsq-self.model_parameters[2])
        rhs += self.model_parameters[3]*wvlsq

        tmp_p = -2*rhs/(1-rhs)
        tmp_q = -1/(1-rhs)

        ref_index = -0.5*tmp_p + np.sqrt(np.power(0.5*tmp_p, 2) - tmp_q)
        return ref_index

class Exotic(Model):

    '''
    requires wavelength input in micrometers
    returns real part of refractive index only
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'wavelength'
        self.required_unit = 'um'
        self.output = 'n'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, wavelengths] = self.preprocess(spectrum)
        rhs = self.model_parameters[0]*ones
        wvlsq = np.power(wavelengths, 2)

        rhs += self.model_parameters[1]*wvlsq/(wvlsq - self.model_parameters[2])
        rhs += (self.model_parameters[3]*(wavelengths -self.model_parameters[4])/
                (np.power(wavelengths - self.model_parameters[4], 2) +
                 self.model_parameters[5]))
        ref_index = np.sqrt(rhs)
        return ref_index

class Drude(Model):

    '''
    requires energy input in eV
    returns real and imaginary parts of permittivity
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'energy'
        self.required_unit = 'ev'
        self.output = 'eps'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, energies] = self.preprocess(spectrum)
        omega_p = self.model_parameters[0] # plasma frequency in eV
        loss = self.model_parameters[1] # loss in eV
        return ones - omega_p**2/(np.power(energies, 2)+1j*loss*energies)

class DrudeLorentz(Model):

    '''
    requires energy input in eV
    returns real and imaginary parts of permittivity
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'energy'
        self.required_unit = 'ev'
        self.output = 'eps'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, energies] = self.preprocess(spectrum)
        omega_p = self.model_parameters[0] # plasma frequency in eV
        w_res = self.model_parameters[1] # frequency of Lorentz pole in eV
        loss = self.model_parameters[2] # loss in eV
        return ones - omega_p**2/((np.power(energies, 2)-w_res**2)+1j*loss*energies)


class Fano(Model):

    '''
    this model can be applied to scattering cross sections
    requires energy input in eV
    returns real and imaginary parts of permittivity
    '''
    def input_output(self):
        """defines the required inputs and the output spectrum type"""
        self.required_spectrum_type = 'energy'
        self.required_unit = 'ev'
        self.output = 'scattering_cross_setion'

    def evaluate(self, spectrum):
        """returns the value of the spectral data for the given spectrum"""
        [ones, energies] = self.preprocess(spectrum)
        q = self.model_parameters[0] # Fano parameter
        e_r = self.model_parameters[1] # resonant energy in eV
        gamma = self.model_parameters[2] # loss in eV
        epsilon =  2*(energies-e_r)/gamma
        #loss = self.model_parameters[1] # loss in eV
        norm = (1+q**2)
        sigma = (1/norm) *(epsilon+q)**2 / (epsilon**2+1)
        return sigma
