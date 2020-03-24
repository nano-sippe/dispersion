"""material_data implements the MaterialData class which can hold different
representations of spectral data (e.g. refractive index of permittivity).
The data is in the form of either a constant value, tabulated data or a model.
These different representations can be combined e.g. model for n (real part
of refractive index) and constant value for k (imaginary part of refractive
index)
"""

from __future__ import print_function
import os
#import sys
import codecs
import numpy as np
#import matplotlib.pyplot as plt
from refractive_index_database.spectrum import Spectrum
from refractive_index_database.spectral_data import Constant, Interpolation, \
                                                    Extrapolation
import refractive_index_database.spectral_data as spectral_data
from refractive_index_database.io import Reader



def validate_table(tabulated_data):
    '''
    check that spectral part (first column) is
    monotonically increasing to be able to interpolate
    '''
    return np.all(tabulated_data[1:, 0] > tabulated_data[:-1, 0])


def fix_table(tabulated_data):
    '''
    throw out rows which break strict monotonicity
    '''
    n_cols = tabulated_data.shape[1]
    new_rows = [tabulated_data[0, :]]
    last_valid = tabulated_data[0, 0]
    for row in range(1, tabulated_data.shape[0]):
        if not tabulated_data[row, 0] > last_valid:
            continue
        else:
            new_rows.append(tabulated_data[row, :])
            last_valid = tabulated_data[row, 0]
    return np.array(new_rows).reshape(-1, n_cols)


def process_tabulated_data(table):
    '''
    takes tabulated data in string form
    and converts to a numpy array
    '''

    if isinstance(table, np.ndarray):
        numeric_table = table
    elif isinstance(table, str):
        #table is a str
        numeric_table = []
        for row in table.split('\n'):
            if row.isspace() or row == "":
                break
            numeric_col = []
            for col in row.split():
                numeric_col.append(float(col))
            numeric_table.append(numeric_col)
        numeric_table = np.array(numeric_table)

    else:
        raise TypeError("table of type " +
                        "{} cannot be parsed".format(type(table)))
    if validate_table(numeric_table) is False:
        numeric_table = fix_table(numeric_table)
    return numeric_table


class MaterialData(object):
    '''
    Class for processing data from files into
    a model for n and k (or eps_r and eps_i)

    mutually exclusive arguments:
      file_path(str): file path to load data from
      fixed_n(float): fixed real part of refractive index
      fixed_nk(complex): fixed complex refractive index
      fixed_eps_r(float): fixed real part of permittivity
      fixed_eps(complex): fixed complex permittivity
      model_kw(dict): dictionary with information for model
                      see _process_model_dict
    other arguments:
      spectrum_type(str): sets the default spectrum type
      unit(str): sets the default unit
    '''

    def __init__(self, **kwargs):
        #parsing arguments
        parsed_args = self._parse_args(kwargs)
        #set inputs and defaults
        file_path = parsed_args["file_path"]
        #self.meta_data = None
        self.meta_data = {}
        self.meta_data['Reference'] = ""
        self.meta_data['Comment'] = ""
        self.meta_data['Name'] = ""
        self.meta_data['FullName'] = ""
        self.meta_data['Author'] = ""
        self.meta_data['Alias'] = ""
        self._file_data = None
        self.data = {'name': "",
                     'real': None,
                     'imag': None,
                     'complex':None}
        self.options = {'InterpOrder':'cubic'}
        self.defaults = {'unit':parsed_args["unit"],
                         'spectrum_type':parsed_args["spectrum_type"]}

        #process input arguments
        if file_path is not None:
            reader = Reader(file_path)
            file_data = reader.read_file()
            self._process_file_data(file_data)
        elif parsed_args['model_kw'] is not None:
            self._process_model_dict(parsed_args['model_kw'])
        else:
            self._process_fixed_value(parsed_args)

        self._complete_partial_data()

    def _parse_args(self, args):
        """
        validated the dictionary of class inputs
        """
        mutually_exclusive = {"file_path", "fixed_n", "fixed_nk",
                              "fixed_eps_r", "fixed_eps",
                              "model_kw"}
        inputs = {}
        n_mutually_exclusive = 0
        for arg in args.keys():
            if arg in args and args[arg] is not None:
                if arg in mutually_exclusive:
                    n_mutually_exclusive += 1
            inputs[arg] = args[arg]

        if n_mutually_exclusive == 0:
            raise ValueError("At least one of the following" +
                             " inputs is required: "+
                             "{}".format(mutually_exclusive))
        elif n_mutually_exclusive > 1:
            raise ValueError("Only one of the following" +
                             "inputs is allowed: "+
                             "{}".format(mutually_exclusive))
        # Check types
        str_args = {'file_path', 'spectrum_type', 'unit'}
        str_types = {str}
        self._check_type(inputs, str_args, str_types)
        if inputs['spectrum_type'] is None :
            inputs['spectrum_type'] = 'wavelength'
        if inputs['unit'] is None:
            inputs['unit'] = 'nanometer'
        # pylint: disable=no-member
        # bug in pylint does not recognise numpy data types
        float_args = {"fixed_n", "fixed_eps_r"}
        float_types = {float, np.double}
        self._check_type(inputs, float_args, float_types)

        complex_args = {"fixed_nk", "fixed_eps"}
        complex_types = {complex, np.cdouble}
        self._check_type(inputs, complex_args, complex_types)

        dict_args = {'model_kw'}
        dict_types = {dict}
        self._check_type(inputs, dict_args, dict_types)
        return inputs

    @staticmethod
    def _check_type(args, names, types):
        """
        raises TypeError if the names keys in args dict are not in the
        set of types. If name is not in args, place a default value of None.
        """
        for arg in names:
            if arg in args and args[arg] is not None:
                invalid_type = False
                for _type in types:
                    if isinstance(args[arg], _type):
                        invalid_type = True
                if invalid_type is False:
                    raise TypeError("argument " +
                                    "{} must be".format(arg) +
                                    " of types: {}".format(types))
            else:
                args[arg] = None


    def _complete_partial_data(self):
        """
        if only partial data was provided then set remaining parameters
        to constant value of 0.
        """
        if self.data['real'] is None:
            self.data['real'] = Constant(0.0)
        if self.data['imag'] is None:
            self.data['imag'] = Constant(0.0)

    def remove_absorption(self):
        """
        sets loss (k or epsi) to constant zero value
        """
        self.data['imag'] = Constant(0.0)

    def extrapolate(self,new_spectrum,spline_order=2):
        """
        extrapolates the material data for cover the range defined by the
        spectrum new_spectrum. if new_spectrum has only one element, the data
        will be extrapolated from the relevant end of its valid range up to the
        value given by new_spectrum. spline_order defines the order of the
        spline used for extrapolation. The results of the extrapolation depend
        heavily on the order chosen, so please check the end result to make
        sure it make physical sense.
        """

        if self.data['complex'] is None:
            for data_name in ['real','imag']:
                if isinstance(self.data[data_name],Constant):
                    continue
                self.data[data_name] = Extrapolation(self.data[data_name],
                                                     new_spectrum,
                                                     spline_order=spline_order)
        else:
            raise NotImplementedError("extrapolation not implemented " +
                                      "for materials with real and imaginary "+
                                      "parts not independent from each other")

    def _process_fixed_value(self, input_dict):
        '''
        use fixed value input to set n/k
        or permittivity to SpectralData.Constant objects
        '''
        if input_dict['fixed_n'] is not None:
            self.data['name'] = 'nk'
            self.data['real'] = Constant(input_dict['fixed_n'])
            #self._k = Constant(0.0)
        elif input_dict['fixed_nk'] is not None:
            self.data['name'] = 'nk'
            self.data['real'] = Constant(np.real(input_dict['fixed_nk']))
            self.data['imag'] = Constant(np.imag(input_dict['fixed_nk']))
        elif input_dict['fixed_eps_r'] is not None:
            self.data['name'] = 'eps'
            self.data['real'] = Constant(input_dict['fixed_eps_r'])
            #self._epsi = Constant(0.0)
        elif input_dict['fixed_eps'] is not None:
            self.data['name'] = 'eps'
            self.data['real'] = Constant(np.real(input_dict['fixed_eps']))
            self.data['imag'] = Constant(np.imag(input_dict['fixed_eps']))
        else:
            raise RuntimeError("Failed to set a constant value for n,k or eps")

    def _process_model_dict(self, model_dict):
        """
        use dict to return a SpectralData.Model object and sets the relevant
        n/k or permittivity class attributes

        dict items:
        name(str): class name of the model (see spectral_data.py)
        spectrum_type(str): spectrum Type (see spctrum.py)
        unit(str): spetrum unit (see spctrum.py)
        valid_range(np.array): min and max of the spectral range
                              for which the model is valid
        parameters(np.array): all paramters (i.e. coefficients)
                              needed for the model
        """
        model_class = self._str_to_class(model_dict['name'])
        kws = {}
        if "spectrum_type" in model_dict:
            kws['spectrum_type'] = model_dict['spectrum_type']
            self.defaults['spectrum_type'] = model_dict['spectrum_type']
        if "unit" in model_dict:
            kws['unit'] = model_dict['unit']
            self.defaults['unit'] = model_dict['unit']


        model = model_class(model_dict['parameters'],
                            model_dict['valid_range'], **kws)

        if model.output == 'n':
            self.data['name'] = 'nk'
            self.data['real'] = model
        elif model.output == 'k':
            self.data['name'] = 'nk'
            self.data['imag'] = model
        elif model.output == 'nk':
            self.data['name'] = 'nk'
            self.data['complex'] = model
        elif model.output == 'epsr':
            self.data['name'] = 'eps'
            self.data['real'] = model
        elif model.output == 'epsi':
            self.data['name'] = 'eps'
            self.data['imag'] = model
        elif model.output == 'eps':
            self.data['name'] = 'eps'
            self.data['complex'] = model
        else:
            raise ValueError("model output <{}> invalid".format(model.output))

    @staticmethod
    def _str_to_class(field):
        """
        tries to evaluate the given string as a class from the spectral_data
        module
        """
        try:
            identifier = getattr(spectral_data, field)
        except AttributeError:
            raise NameError("%s doesn't exist." % field)
        if isinstance(identifier, type):
            return identifier
        raise TypeError("%s is not a class." % field)

    def _process_file_data(self, file_dict):
        """
        uses dictionary of string values in file_dict
        to set relevant class attributes
        """
        self._file_data = file_dict
        self.meta_data = {}
        self.meta_data['Reference'] = file_dict['MetaData']['Reference']
        self.meta_data['Comment'] = file_dict['MetaData']['Comment']
        self.meta_data['Name'] = file_dict['MetaData']['Name']
        self.meta_data['FullName'] = file_dict['MetaData']['FullName']
        self.meta_data['Author'] = file_dict['MetaData']['Author']

        datasets = file_dict['Datasets']
        #self.dataTypes = []
        #self.dataSets = []
        for dataset in datasets:
            data_type, identifier = dataset['MetaData']['DataType'].split()
            meta_data = dataset['MetaData']

            if data_type == 'tabulated':
                #data is tabulated
                processed = process_tabulated_data(dataset['Data'])
            elif data_type == 'formula' or data_type == 'model':
                #data is a formula with coefficients
                self._process_formula_data(dataset)
            else:
                raise ValueError("data type {} not supported".format(data_type))

            if data_type == 'tabulated':
                if (meta_data['SpectrumType'] and \
                    meta_data['SpectrumType'] is not None):
                    self.defaults['spectrum_type'] = meta_data['SpectrumType']
                if (meta_data['Unit'] and \
                    meta_data['Unit'] is not None):
                    self.defaults['unit'] = meta_data['Unit']
                sp_dat_fr_tb = self._spec_data_from_table
                if identifier == 'nk':
                    self.data['name'] = 'nk'
                    self.data['real'] = sp_dat_fr_tb(processed[:, [0, 1]])
                    self.data['imag'] = sp_dat_fr_tb(processed[:, [0, 2]])
                elif identifier == 'n':
                    self.data['name'] = 'nk'
                    self.data['real'] = sp_dat_fr_tb(processed)
                elif identifier == 'k':
                    self.data['name'] = 'nk'
                    self.data['imag'] = sp_dat_fr_tb(processed)



    def _spec_data_from_table(self, data):
        '''
        using first column of data, convert values
        into a SpectralData object
        '''
        n_rows = data.shape[0]
        spec_type = self.defaults['spectrum_type']
        unit = self.defaults['unit']
        if n_rows == 1:
            return Constant(data[0, 1],
                            valid_range=(data[0, 0], data[0, 0]),
                            spectrum_type=spec_type, unit=unit)

        return Interpolation(data, spectrum_type=spec_type,
                             unit=unit)

    def _process_formula_data(self, data_dict):
        '''
        create model_dict and call process_model_dict
        use range and coefficients in input dictionary
        to return a SpectralData.Model
        '''
        model_dict = {}
        meta_data = data_dict['MetaData']
        data_type, identifier = meta_data['DataType'].split()
        if not (data_type == 'formula' or data_type == 'mode'):
            raise ValueError("dataType <{}> not a valid formula or model")
        if data_type == 'formula':
            identifier = int(identifier)

        if meta_data['ValidRange']:
            valid_range = meta_data['ValidRange'].split()

        for i_valid_range, v_range in enumerate(valid_range):
            valid_range[i_valid_range] = float(v_range)
        model_dict['valid_range'] = valid_range

        coefficients = data_dict['Data'].split()
        for iter_coeff, coeff in enumerate(coefficients):
            coefficients[iter_coeff] = float(coeff)
        model_dict['parameters'] = np.array(coefficients)


        if meta_data['SpectrumType']:
            model_dict['spectrum_type'] = meta_data['SpectrumType']
        else:
            model_dict['spectrum_type'] = self.defaults['spectrum_type']

        if meta_data['Unit']:
            model_dict['unit'] = meta_data['Unit']
        else:
            model_dict['unit'] = self.defaults['unit']

        method_ids = {1: 'Sellmeier', 2: 'Sellmeier2',
                      3: 'Polynomial', 4: 'RefractiveIndexInfo',
                      5: 'Cauchy', 6: 'Gases',
                      7: 'Herzberger', 8: 'Retro',
                      9: 'Exotic'}

        if isinstance(identifier, int):
            model_dict['name'] = method_ids[identifier]
        else:
            model_dict['name'] = identifier

        self._process_model_dict(model_dict)


    def get_nk_data(self, spectrum_values,
                    spectrum_type='wavelength',
                    unit='meter'):
        '''
        return complex refractive index for a given input
        spectrum.


        spectrum_type = wavelength | frequency | energy
        for more information see SpectralData.py

        unit = meter|nanometer|micrometer|hertz|electronvolt

        '''
        if isinstance(spectrum_values, Spectrum):
            spectrum = spectrum_values
        else:
            spectrum = Spectrum(spectrum_values,
                                spectrum_type=spectrum_type,
                                unit=unit)

        if not (self.data['name'] == 'nk' or self.data['name'] == 'eps'):
            raise ValueError("data type {}".format(self.data['name']) +
                             "cannot be converted to refractive index")

        if self.data['complex'] is None:
            real = self.data['real'].evaluate(spectrum)
            imag = 1j*self.data['imag'].evaluate(spectrum)
            complex_val = real+imag
        else:
            complex_val = self.data['complex'].evaluate(spectrum)

        if self.data['name'] == 'eps':
            complex_val = np.sqrt(complex_val)
        return complex_val

    def get_permittivity(self, spectrum_values,
                         spectrum_type='wavelength',
                         unit='meter'):
        '''
        return complex permittivity for a given input
        spectrum.


        spectrum_type = wavelength | frequency | energy
        for more information see SpectralData.py

        unit = meter|nanometer|micrometer|hertz|electronvolt

        '''

        if isinstance(spectrum_values, Spectrum):
            spectrum = spectrum_values
        else:
            spectrum = Spectrum(spectrum_values,
                                spectrum_type=spectrum_type,
                                unit=unit)

        if not (self.data['name'] == 'nk' or self.data['name'] == 'eps'):
            raise ValueError("data type {}".format(self.data['name']) +
                             "cannot be converted to refractive index")

        if self.data['complex'] is None:
            real = self.data['real'].evaluate(spectrum)
            imag = 1j*self.data['imag'].evaluate(spectrum)
            complex_val = real+imag
        else:
            complex_val = self.data['complex'].evaluate(spectrum)

        if self.data['name'] == 'nk':
            complex_val = np.power(complex_val, 2)
        return complex_val

    def get_maximum_valid_range(self):
        """
        checks both real and imaginary parts of spectral data and finds the
        maximum spectral range which is valid for both parts.
        """
        if not(self.data['name'] == 'nk' or self.data['name'] == 'eps'):
            raise RuntimeError("valid_range cannot be defined as "+
                               "MaterialData does not yet contain "+
                               " a valid n/k or permittivity spectrum")

        if self.data['complex'] is None:
            real_lower = np.min(self.data['real'].valid_range.values)
            real_upper = np.max(self.data['real'].valid_range.values)
            imag_lower = np.min(self.data['imag'].valid_range.values)
            imag_upper = np.max(self.data['imag'].valid_range.values)
            lower = np.max([real_lower, imag_lower])
            upper = np.min([real_upper, imag_upper])
        else:
            lower = np.min(self.data['complex'].valid_range.values)
            upper = np.max(self.data['complex'].valid_range.values)
        return np.array([lower, upper])

    @staticmethod
    def utf8_to_ascii(string):
        """converts a string from utf8 to ascii"""
        uni_str = codecs.encode(string, 'utf-8')
        ascii_str = codecs.decode(uni_str, 'ascii', 'ignore')
        return ascii_str

    def print_reference(self):
        """print material reference"""
        print(self.utf8_to_ascii(self.meta_data['Reference']))

    def print_comment(self):
        """print material comment"""
        print(self.utf8_to_ascii(self.meta_data['Comment']))


    def plot_nk_data(self, **kwargs):
        """plots the real and imaginary part of the refractive index"""
        raise NotImplementedError("plotting disabled to remove" +
                                  "matplotlib dependence")
        self._plot_data('nk', **kwargs)

    def plot_permittivity(self, **kwargs):
        """plots the real and imaginary part of the permittivity"""
        raise NotImplementedError("plotting disabled to remove" +
                                  "matplotlib dependence")
        self._plot_data('permittivity', **kwargs)

    def _plot_data(self, data_label, **kwargs):
        """internal function used for plotting spectral data"""
        import matplotlib.pyplot as plt

        plot_data = self._prepare_plot_data(**kwargs)
        if 'axes' not in kwargs:
            plot_data['axes'] = plt.axes()
        else:
            plot_data['axes'] = kwargs['axes']
        if data_label == 'nk':
            data = self.get_nk_data(plot_data['spectrum'])
            labels = ['n', 'k']
        elif data_label == 'permittivity':
            data = self.get_permittivity(plot_data['spectrum'])
            labels = ['eps_r', 'eps_i']

        data_r = np.real(data)
        data_i = np.imag(data)
        # pylint: disable=protected-access
        # this is the only way to access the color cycler
        axes = plot_data['axes']
        spectrum = plot_data['spectrum']
        if spectrum.values.size == 1:
            color = next(axes._get_lines.prop_cycler)['color']
            plt.axhline(data_r, label=labels[0], color=color)
            color = next(axes._get_lines.prop_cycler)['color']
            plt.axhline(data_i, label=labels[1], ls='--', color=color)
        else:
            plt.plot(spectrum.values, data_r, label=labels[0])
            plt.plot(spectrum.values, data_i, ls='--', label=labels[1])
        plt.legend(loc='best')
        plt.ylabel("{}, {}".format(labels[0], labels[1]))
        xlabel = spectrum.get_type_unit_string()
        plt.xlabel(xlabel)

    def _prepare_plot_data(self, **kwargs):
        """internal function to prepare data for plotting"""
        plot_data = {}
        if 'spectrum_type' not in kwargs:
            plot_data['spectrum_type'] = self.defaults['spectrum_type']
        else:
            plot_data['spectrum_type'] = kwargs['spectrum_type']
        if 'unit' not in kwargs:
            plot_data['unit'] = self.defaults['unit']
        else:
            plot_data['unit'] = kwargs['unit']
        if 'values' not in kwargs:
            spectrum = self.get_sample_spectrum()
            values = spectrum.convert_to(plot_data['spectrum_type'],
                                         plot_data['unit'])


        else:
            values = kwargs['values']
            if isinstance(values, (list, tuple)):
                values = np.array(values)
        spectrum = Spectrum(values,
                            spectrum_type=plot_data['spectrum_type'],
                            unit=plot_data['unit'])
        plot_data['spectrum'] = spectrum
        return plot_data

    def get_sample_spectrum(self):
        """creates a spectrum which covers the maximum valid range
        of the material data"""
        max_range = self.get_maximum_valid_range()
        if max_range[0] == 0.0 or max_range[1] == np.inf:
            values = np.geomspace(100, 2000, 1000)
            spectrum = Spectrum(values, spectrum_type='wavelength',
                                unit='nm')
        else:
            values = np.geomspace(max_range[0], max_range[1], 1000)
            if values[0] < max_range[0]:
                values[0] = max_range[0]
            if values[-1] > max_range[1]:
                values[-1] = max_range[1]
            spectrum = Spectrum(values,
                                spectrum_type=self.defaults['spectrum_type'],
                                unit=self.defaults['unit'])
        return spectrum


if __name__ == "__main__":
    #mat = MaterialData(file_path="./Material_Data/Aluminum.txt")
    #print(mat.get_nk_data(0.5))
    """
    fig = plt.figure()
    axes = plt.gca()
    mat = MaterialData(fixed_n=1.5)
    print(mat.get_maximum_valid_range())
    mat.plot_permittivity(axes=axes)
    #mat.plot_nk_data(axes=axes)
    #print(mat.get_nk_data(0.5, spectrum_type='energy', unit='eV'))
    #mat = MaterialData(fixed_eps=1.5+3j)
    #print(mat.get_permittivity(1.0))
    basePath = "/data/numerik/bzfmanle/Simulations/pypmj/database"
    filename = "RefractiveIndexInfo/main/Au/Rakic.yml"
    mat = MaterialData(file_path=os.path.join(basePath, filename),
                       unit='micrometer')
    print(mat.get_maximum_valid_range())
    print(mat.get_nk_data(0.5, unit='micrometer'))
    mat.plot_permittivity(axes=axes)
    #mat.plot_nk_data(axes=axes)
    eVs = np.linspace(0.5, 1.5, 100)

    #mat.plot_nk_data(axes=axes, values=eVs, spectrum_type='energy', unit='ev')
    plt.show()
    """

    #print(mat.get_nk_data(np.linspace(0.8, 1.0, 3), spectrum_type='energy', unit='eV'))
    #print(mat.get_nk_data(3e14, spectrum_type='frequency', unit='Hz'))

    #mat = MaterialData(file_path="./RefractiveIndexInfo/main/Cu/Brimhall.yml",
    #                   unit='micrometer')
    #print(mat.get_maximum_valid_range())
    #print(mat.get_nk_data(12, unit='nanometer'))

    #mat = MaterialData(file_path="./RefractiveIndexInfo/main/SiO2/Gao.yml",
    #                   unit='micrometer')
    #print(mat.get_maximum_valid_range())
    #print(mat.get_nk_data(500, unit='nanometer'))

    #mat = MaterialData(file_path="./RefractiveIndexInfo/other/commercial plastics/CR-39/poly.yml",
    #                   unit='micrometer')
    #print(mat.get_maximum_valid_range())
    #print(mat.get_nk_data(589.29, unit='nanometer'))

    #print(mat.get_permittivity(0.5))
    #mat = MaterialData(file_path="./RefractiveIndexInfo/main/SiO2/Malitson.yml")
    #print(mat.get_nk_data(0.5e-6))
    #print(mat.get_permittivity(0.5e-6))
