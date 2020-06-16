"""provides functions for reading and writing files.

implements a set of functions for reading and writing yaml files. Also
implements a reader and writer object for interfacing with material data files.

Functions
---------
read_yaml_file
    convert a file with yaml format to dict
read_yaml_string
    convert a string with yaml format to dict
write_yaml_file
    write dict to a yaml format file
print_yaml_string
    print a dict in yaml format to stdout

Classes
-------
Reader
    reads refractive index data from file
Writer
    writes refractive index data to file
"""
import os
import sys
import codecs
import warnings
import numpy as np
from collections import OrderedDict

USE_RUAMEL = True
try:
    from ruamel.yaml import YAML
except ModuleNotFoundError as exc:
    warnings.warn("preferred yaml package ruamel.yaml not installed, falling" +
                  " back to PyYAML, writing yaml files may give inconsistent" +
                  " round trip results")
    USE_RUAMEL = False
    import yaml

def read_yaml_file(file_path):
    """opens yaml file and returns contents as a dict like.

    Parameters
    ----------
    file_path: str
        path to the yaml file

    Returns
    -------
    dict or OrderedDict
        the data from the yaml file

    Notes
    -----
    If USE_RUAMEL is true an OrderedDict is returned, otherwise a dict is
    returned.
    """
    with open(file_path, 'r', encoding="utf-8") as fpt:
        if USE_RUAMEL:
            yaml_obj = YAML()
            yaml_data = yaml_obj.load(fpt)
        else:
            yaml_data = yaml.load(fpt)
    return yaml_data

def read_yaml_string(string_data):
    """converts a string in yaml format to a dict like.

    Parameters
    ----------
    string_data: str
        string in the yaml format

    Returns
    -------
    dict or OrderedDict
        the data from the yaml file

    Warnings
    --------
    No attempt is made to check if string_data is in correct yaml format.

    Notes
    -----
    If USE_RUAMEL is true an OrderedDict is returned, otherwise a dict is
    returned.
    """
    if USE_RUAMEL:
        yaml_obj = YAML()
        yaml_data = yaml_obj.load(string_data)
    else:
        yaml_data = yaml.load(string_data)
    return yaml_data

def write_yaml_file(file_path, dict_like):
    """write a dict_like object to a file using the given file path.

    Parameters
    ----------
    file_path: str
        path with file name and extension
    dict_like: dict or OrderedDict
        the data to be written to file
    """
    with open(file_path, 'w') as fpt:
        if USE_RUAMEL:
            yaml_obj = YAML()
            yaml_obj.dump(dict_like, fpt)
        else:
            yaml.dump(dict_like, fpt)

def print_yaml_string(dict_like):
    """print a dict_like object to stdout in yaml format.

    Parameters
    ----------
    dict_like: dict or OrderedDict
        the data to be written to printed
    """
    if USE_RUAMEL:
        yaml_obj = YAML()
        yaml_obj.dump(dict_like, sys.stdout)
    else:
        print(yaml.dump(dict_like))

class Reader():
    """interface for reading refractive index data from file.

    Attributes
    ----------
    file_path: str
        path to the file to be read
    extension: str
        file type to read
    default_file_dict: dict
        default values to use

    Methods
    -------
    read_file
        read the associated file
    """

    FILE_META_DATA_KEYS = {"Comment", "Reference", "Author",
                           "Name", "FullName"}

    DATASET_META_DATA_KEYS = {'ValidRange', 'DataType',
                              'SpectrumType', 'Unit'}

    def __init__(self, file_path):
        self.file_path = file_path
        fname, extension = os.path.splitext(file_path)
        self.extension = extension
        self.default_file_dict = self._create_default_file_dict()

    def _create_default_file_dict(self):
        """default values for the material data."""
        file_dict = {'MetaData': {}}
        for mdk in Reader.FILE_META_DATA_KEYS:
            file_dict['MetaData'][mdk] = ""
        file_dict['Datasets'] = [Reader._create_default_data_dict()]
        file_dict['Specification'] = {}
        file_dict['MetaComment'] = ""
        file_dict['FilePath'] = self.file_path
        return file_dict

    @staticmethod
    def _create_default_data_dict():
        """default values for a data set."""
        dataset_dict = {'MetaData': {}}
        for mdk in Reader.DATASET_META_DATA_KEYS:
            dataset_dict['MetaData'][mdk] = ""
        dataset_dict['Data'] = []
        return dataset_dict

    def read_file(self):
        """reads the material data file from file.

        Returns
        -------
        dict
            the data from the material file
        """
        txt_types = {'.txt', '.csv'}
        if self.extension in txt_types:
            return self._read_text_file()
        elif self.extension == '.yml':
            return self._read_yaml_mat_file()
        else:
            raise ValueError("extension " +
                             "{} not supported".format(self.extension) +
                             ", supported extensions are (.yml|.csv|.txt)")

    def _read_text_data(self):
        """read data stored in a .txt or .csv file."""
        fname, ext = os.path.splitext(self.file_path)
        try:
            if ext == '.txt':
                data = np.loadtxt(self.file_path, encoding='utf-8')
            elif ext == '.csv':
                data = np.loadtxt(self.file_path, encoding='utf-8',
                                  delimiter=',')
        except IOError as exc:
            raise exc
        data_dict = self._create_default_data_dict()
        data_dict['MetaData']['DataType'] = 'tabulated nk'
        data_dict['Data'] = data
        return data_dict

    def _read_text_comment(self):
        '''
        returns text from contiguous lines in file beginning with #.
        '''
        comment = []
        with codecs.open(self.file_path, 'r', 'utf-8') as fpt:
            for line in fpt:
                if line[0] == "#":
                    comment.append(line[1:].rstrip("\n\r"))
                else:
                    return comment
        return comment

    def _read_text_file(self):
        """
        text files (.txt,.csv) may only contain tabulated nk data
        plus metadata. Metadata should be at the beginning of the
        file, one item per line. The line must start with '#' to
        denote metadata. Metadata is written in the key:value
        structure.
        """

        dataset = self._read_text_data()
        comment = self._read_text_comment()
        file_dict = dict(self.default_file_dict)
        file_dict['Datasets'][0] = dataset
        multi_line_comment = ""
        for line in comment:
            kwd_arg = line.split(":")
            if len(kwd_arg) == 1:
                multi_line_comment += line
            elif len(kwd_arg) == 2:
                kwd = kwd_arg[0].upper()
                arg = kwd_arg[1].rstrip("\n\r").lstrip()
                valid = False
                for key in Reader.FILE_META_DATA_KEYS:
                    if kwd.startswith(key.upper()):
                        file_dict['MetaData'][key] = arg
                        valid = True
                        break
                if valid is False:
                    for key in Reader.DATASET_META_DATA_KEYS:
                        if kwd.startswith(key.upper()):
                            file_dict['Datasets'][0]['MetaData'][key] = arg
                            valid = True
                            break
                if valid is False:
                    KeyError("keyword " +
                             "[{}] in comment header invalid".format(kwd))
            else:
                raise RuntimeError(" string \":\" may only appear" +
                                   "once per line in comment header")
        if multi_line_comment != "":
            file_dict['MetaComment'] = multi_line_comment
        return file_dict

    def _read_yaml_mat_file(self):
        '''
        The refractiveindex.info database format
        '''
        #yaml_stream = open(self.file_path, 'r', encoding="utf-8")
        #dir_path = os.path.dirname(os.path.realpath(__file__))
        yaml_data = read_yaml_file(self.file_path)

        file_dict = dict(self.default_file_dict)
        file_dict = self._process_mat_dict(file_dict, yaml_data)
        file_dict['MetaComment'] = self._read_text_comment()
        return file_dict

    def _process_mat_dict(self, file_dict, yaml_dict):
        """
        copies raw data from a yaml file to the format used in this package.

        Parameters
        ----------
        file_dict: dict
            dict with the correct field names for creating a materialdata object
        yaml_dict: dict
            dict with the raw data describing a material

        Returns
        -------
        dict
            the updated file_dict
        """
        for kwd in yaml_dict:
            kwd = kwd.upper()
            arg = yaml_dict[kwd]
            valid = False
            if kwd == 'DATA':
                valid = True
                file_dict['Datasets'] = self._process_mat_data_dict(arg)
            elif kwd == 'SPECS':
                valid = True
                file_dict['Specification'] = arg
            if valid is False:
                for key in Reader.FILE_META_DATA_KEYS:
                    if kwd.startswith(key.upper()):
                        file_dict['MetaData'][key] = arg
                        valid = True
                        break
            if valid is False:
                KeyError("keyword [{}] in file invalid".format(kwd))
        return file_dict

    def _process_mat_data_dict(self, mat_data):
        """
        creates a list of dicts to generate spectral data sets

        Parameters
        ----------
        mat_data: list of dicts
            data for creating spectral data sets

        Returns
        -------
        list of dicts
            formated data for use in this package
        """
        aliases = {'ValidRange': {'validRange', 'range',
                                  'spectra_range', 'wavelength_range'}}
        dataset_list = []
        for n_data_set, dataset in enumerate(mat_data):
            dataset_list.append(Reader._create_default_data_dict())
            data_dict = dataset_list[-1]
            data_type = dataset['type'].lstrip()
            data_dict['MetaData']['DataType'] = data_type
            if (data_type.startswith('formula') or
                    data_type.startswith('model')):
                data_dict['Data'] = dataset['coefficients']
            elif data_type.startswith('tabulated'):
                data_dict['Data'] = dataset['data']
            else:
                raise KeyError("data type <{}> invalid".format(data_type))

            for kwd in dataset:
                valid = False
                arg = dataset[kwd]
                kwd = kwd.upper()
                for key in Reader.DATASET_META_DATA_KEYS:
                    if valid:
                        break
                    if key in aliases.keys():
                        all_names = aliases[key]
                    else:
                        all_names = {key}
                    for alias in all_names:
                        if kwd.startswith(alias.upper()):
                            data_dict['MetaData'][key] = arg
                            valid = True
                            break
                if valid is False:
                    KeyError("keyword <{}> in file invalid".format(kwd))
        return dataset_list


class Writer():
    """interface for writing refractive index data to file.

    Attributes
    ----------
    file_path: str
        path to the file to be written
    extension: str
        file type to write
    file_name: str
        name of the file
    material: MaterialData
        the material object to be written

    Methods
    -------
    write_file
        write the material data to file

    Notes
    -----
    if data_dict is not an OrderedDict, the order in which the data and
    metadata is written cannot be controlled.
    """

    KEY_ALIASES = OrderedDict({"Comment": "COMMENTS",
                               "Reference": "REFERENCES",
                               "Specification": "SPECS",
                               "ValidRange": "wavelength_range",
                               "DataType": "type"})

    DATASET_META_DATA_KEYS = ['ValidRange', 'DataType',
                              'SpectrumType', 'Unit']

    def __init__(self, file_path, material):
        self.file_path = file_path
        fname, extension = os.path.splitext(file_path)
        self.extension = extension
        self.file_name = fname
        self.file_dict = material.prepare_file_dict()

    def write_file(self):
        """
        write the data to the file_path
        """
        raise NotImplementedError("writing material files not yet implemented")
        txt_types = {'.txt', '.csv'}
        if self.extension in txt_types:
            return self._write_text_file()
        elif self.extension == '.yml':
            return self._write_yaml_file()
        else:
            raise ValueError("extension" +
                             "{} not supported".format(self.extension) +
                             ", supported extensions are (.yml|.csv|.txt)")

    def _write_text_file(self):
        """
        writer for .txt and .csv files
        """
        header = ""
        for item in Writer.KEY_ALIASES.items():
            header += "#{}: {}".format(item[1], self.file_dict[item[0]])
        #TODO finish function

    def _write_yaml_file(self):
        """
        writer for .yml files
        """
        #TODO finish function
        """
        yamlDict = OrderedDict()
        yamlOrder = ['REFERENCES', 'COMMENTS', 'DATA', 'SPECS']

        for yamlKey in yamlOrder[:2]:
            for key, val in self.file_dict['MetaData'].items():
                if key in Writer.keyAliases:
                    if Writer.keyAliases[key] == yamlKey:
                        print(type(val))
                        yamlDict[yamlKey] = val

        yamlDict['DATA'] = []
        for ids, dataset in enumerate(self.file_dict['Datasets']):
            yamlDataset = {}
            metaData = dataset['MetaData']
            for key, val in metaData.items():
                if key in Writer.keyAliases:
                    yamlDataset[Writer.keyAliases[key]] = val
            yamlDict['DATA'].append(yamlDataset)
            data_type = metaData['DataType'].split()[0]
            if data_type == 'tabulated':
                yamlDataset['data'] = dataset['Data']
            elif data_type == 'formula':
                yamlDataset['coefficients'] = dataset['Data']
        print(yamlDict['REFERENCES'])
        yamlDict['SPECS'] = OrderedDict()

        specOrder = ['n_absolute',
                     'wavelength_vacuum',
                     'film_thickness',
                     'substrate',
                     'temperature',
                     'pressure',
                     'deposition_temperature',
                     'direction']

        for specKey in specOrder:
            for key, val in self.file_dict['Specification'].items():
                if specKey == key:
                    yamlDict['SPECS'][specKey] = val
        with codecs.open(self.file_path, 'w', 'utf-8') as fp:
            for line in self.file_dict['MetaComment']:
                fileLine = "#"+line+"\n"
                fp.write(fileLine)
            fp.write("\n")
            yaml.dump(yamlDict, fp, encoding='utf-8', indent=4,
                      allow_unicode=True,
                      default_flow_style=False,
                      sort_keys=False)
      """
