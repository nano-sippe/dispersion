import os
import numpy as np
import codecs
import pprint
#import yaml
try:
    from ruamel.yaml import YAML
except ModuleNotFoundError as e:
    from ruamel_yaml import YAML
from collections import OrderedDict

"""
def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)


yaml.add_representer(OrderedDict, represent_ordereddict)
"""

class Reader(object):
    """
    class for reading refractive index  data from file.
    """

    FILE_META_DATA_KEYS = {"Comment", "Reference", "Author",
                           "Name", "FullName"}

    DATASET_META_DATA_KEYS = {'ValidRange', 'DataType',
                              'SpectrumType', 'Unit'}

    def __init__(self, file_path):
        self.file_path = file_path
        fname, extension = os.path.splitext(file_path)
        self.extension = extension
        self.default_file_dict = self.create_default_file_dict()


    def create_default_file_dict(self):
        file_dict = {'MetaData': {}}
        for mdk in Reader.FILE_META_DATA_KEYS:
            file_dict['MetaData'][mdk] = ""
        file_dict['Datasets'] = [Reader.create_default_data_dict()]
        file_dict['Specification'] = {}
        file_dict['MetaComment'] = ""
        file_dict['FilePath'] = self.file_path
        return file_dict

    @staticmethod
    def create_default_data_dict():
        dataset_dict = {'MetaData': {}}
        for mdk in Reader.DATASET_META_DATA_KEYS:
            dataset_dict['MetaData'][mdk] = ""
        dataset_dict['Data'] = []
        return dataset_dict

    def read_file(self):
        txt_types = {'.txt', '.csv'}
        if self.extension in txt_types:
            return self.read_text_file()
        elif self.extension == '.yml':
            return self.read_yaml_file()
        else:
            raise ValueError("extension " +
                             "{} not supported".format(self.extension) +
                             ", supported extensions are (.yml|.csv|.txt)")

    def _read_text_data(self):
        fname,ext = os.path.splitext(self.file_path)
        try:
            if ext == '.txt':
                data = np.loadtxt(self.file_path, encoding='utf-8')
            elif ext == '.csv':
                data = np.loadtxt(self.file_path, encoding='utf-8',
                                  delimiter=',')
        except IOError as e:
            raise e
        data_dict = self.create_default_data_dict()
        data_dict['MetaData']['DataType'] = 'tabulated nk'
        data_dict['Data'] = data
        return data_dict

    def _read_text_comment(self):
        '''
        returns text from contiguous lines in file
        beginning with #
        '''
        comment = []
        with codecs.open(self.file_path, 'r', 'utf-8') as fp:
            for line in fp:
                if line[0] == "#":
                    comment.append(line[1:].rstrip("\n\r"))
                else:
                    return comment
        return comment

    def read_text_file(self):
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
        if not multi_line_comment == "":
            file_dict['MetaComment'] = multi_line_comment
        return file_dict

    def read_yaml_file(self):
        '''
        The refractiveindex.info database format
        '''
        #yaml_stream = open(self.file_path, 'r', encoding="utf-8")
        #dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(self.file_path, 'r',encoding="utf-8") as fp:
            yaml = YAML()
            yaml_data = yaml.load(fp)
        file_dict = dict(self.default_file_dict)
        file_dict = self.read_yaml_file_dict(file_dict, yaml_data)
        file_dict['MetaComment'] = self._read_text_comment()
        return file_dict

    def read_yaml_file_dict(self, file_dict, yamlData):
        for kwd in yamlData:
            kwd = kwd.upper()
            arg = yamlData[kwd]
            valid = False
            if kwd == 'DATA':
                valid = True
                file_dict['Datasets'] = self.read_yaml_data_dict(arg)
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

    def read_yaml_data_dict(self, yamlData):
        aliases = {'ValidRange': {'validRange', 'range',
                                  'spectra_range', 'wavelength_range'}}
        nDataSet = 0
        dataset_list = []
        for nDataset, dataset in enumerate(yamlData):
            dataset_list.append(self.create_default_data_dict())
            data_dict = dataset_list[-1]
            dType = dataset['type'].lstrip()
            data_dict['MetaData']['DataType'] = dType
            if (dType.startswith('formula') or
                    dType.startswith('model')):
                data_dict['Data'] = dataset['coefficients']
            elif dType.startswith('tabulated'):
                data_dict['Data'] = dataset['data']
            else:
                raise KeyError("data type <{}> invalid".format(dType))

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


class Writer(object):
    """
    class for writing refractive index data to file.
    """

    KEY_ALIASES = {"Comment": "COMMENTS",
                   "Reference": "REFERENCES",
                   "Specification": "SPECS",
                   "ValidRange": "wavelength_range",
                   "DataType": "type"}

    DATASET_META_DATA_KEYS = {'ValidRange', 'DataType',
                              'SpectrumType', 'Unit'}

    def __init__(self, file_path, data_dict):
        self.file_path = file_path
        fname, extension = os.path.splitext(file_path)
        self.extension = extension
        self.file_name = fname
        self.data_dict = data_dict

    def write_file(self):
        txt_types = {'.txt', '.csv'}
        if self.extension in txt_types:
            return self.writeTextFile()
        elif self.extension == '.yml':
            return self.writeYAMLFile()
        else:
            raise ValueError("extension" +
                             "{} not supported".format(self.extension) +
                             ", supported extensions are (.yml|.csv|.txt)")

    def write_text_file(self):
        pass

    def writeYAMLFile(self):
        pass
        """
        yamlDict = OrderedDict()
        yamlOrder = ['REFERENCES', 'COMMENTS', 'DATA', 'SPECS']

        for yamlKey in yamlOrder[:2]:
            for key, val in self.data_dict['MetaData'].items():
                if key in Writer.keyAliases:
                    if Writer.keyAliases[key] == yamlKey:
                        print(type(val))
                        yamlDict[yamlKey] = val

        yamlDict['DATA'] = []
        for ids, dataset in enumerate(self.data_dict['Datasets']):
            yamlDataset = {}
            metaData = dataset['MetaData']
            for key, val in metaData.items():
                if key in Writer.keyAliases:
                    yamlDataset[Writer.keyAliases[key]] = val
            yamlDict['DATA'].append(yamlDataset)
            dType = metaData['DataType'].split()[0]
            if dType == 'tabulated':
                yamlDataset['data'] = dataset['Data']
            elif dType == 'formula':
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
            for key, val in self.data_dict['Specification'].items():
                if specKey == key:
                    yamlDict['SPECS'][specKey] = val
        with codecs.open(self.file_path, 'w', 'utf-8') as fp:
            for line in self.data_dict['MetaComment']:
                fileLine = "#"+line+"\n"
                fp.write(fileLine)
            fp.write("\n")
            yaml.dump(yamlDict, fp, encoding='utf-8', indent=4,
                      allow_unicode=True,
                      default_flow_style=False,
                      sort_keys=False)
      """
