""" implements the MaterialDatabase class used for administering a
set of data files on disk which describe spectrally resolved
refractive index or permittivity data
"""
from __future__ import print_function
import os
import codecs
#import yaml
import numpy as np
try:
    from ruamel.yaml import YAML
except ModuleNotFoundError as e:
    from ruamel_yaml import YAML
import pandas as pd
from refractive_index_database.material_data import MaterialData
from refractive_index_database.spectrum import Spectrum

def validate_config(config):
    """
    validates all values of the of given MaterialDatabase config        
    """
    check_type(config['Path'],str)
    if not os.path.isdir(config['Path']):
        raise IOError("directory path for database file system is invalid:" +
                      " <{}>".format(config['Path']))
    check_type(config['Interactive'],bool)
    assert "Modules" in config
    for value in config['Modules'].values():
        check_type(value,bool)
    assert "ReferenceSpectrum" in config
    ref_spec = config['ReferenceSpectrum']
    check_type(ref_spec['Value'],float)
    check_type(ref_spec['SpectrumType'],str)
    check_type(ref_spec['Unit'],str)

def check_type(value,val_type):
    """
    checks if value isinstance of val_type, if not raise exception
    """
    if not isinstance(value,val_type):
        raise ValueError("config file data {}".format(value) +
                         "must be of type {}".format(val_type) +
                         ", not {}".format(type(value)))

class MaterialDatabase(object):
    """
    class used for administering a set of data files
    set of data files on disk which describe spectrally resolved
    refractive index or permittivity data
    """
    # pylint: disable=no-member
    # bug in pylint does not recognise numpy data types

    META_DATA = {'Alias':str,
                 'Name':str,
                 'FullName':str,
                 'Author':str,
                 'Comment':str,
                 'Reference':str,
                 'SpectrumType':str,
                 'Unit':str,
                 'SpectrumLowerBound':np.double,
                 'SpectrumUpperBound':np.double,
                 'N_Reference':np.double,
                 'K_Reference':np.double,
                 'Path':str,
                 'Database':str}
    NA_VALUES = {'N_Reference':[""],
                 'K_Reference':[""]}


    def __init__(self, config, rebuild=False):
        validate_config(config)
        self.make_reference_spectrum(config)
        self.config = config
        self.base_path = config['Path']
        if rebuild:
            self.build_database(config['Modules'])
        else:
            dtypes = MaterialDatabase.META_DATA
            self.database = pd.read_csv(os.path.join(self.base_path,
                                                     'database.csv'),
                                        dtype=dtypes,
                                        na_values=MaterialDatabase.NA_VALUES,
                                        keep_default_na=False)
        self.qgrid_widget = None
        if self.config['Interactive']:
            import qgrid
            self.make_qgrid = qgrid.show_grid

    def build_database(self, modules):
        """
        read all modules specified in config and add them to the database
        """
        self.database = pd.DataFrame(columns=MaterialDatabase.META_DATA.keys())
        if modules['RefractiveIndexInfo']:
            refinfo_path = 'RefractiveIndexInfo'
            print("Building RefractiveIndex.info database")
            dir_path = os.path.join(self.base_path, refinfo_path)
            dframe = self.read_refractive_index_info_db(dir_path)
            self.database = self.database.append(dframe, sort=False)
        if modules['Filmetrics']:
            print("Building Filmetrics database")
            filmmetrics_path = 'Filmetrics'
            dir_path = os.path.join(self.base_path, filmmetrics_path)
            dframe = self.read_filmmetrics_db(dir_path)
            self.database = self.database.append(dframe, sort=False)
        if modules['UserData']:
            print("Building UserData database")
            user_data_path = 'UserData'
            dir_path = os.path.join(self.base_path, user_data_path)
            dframe = self.read_user_data_db(dir_path)
            self.database = self.database.append(dframe, sort=False)

    def view_interactive(self):
        """
        returns a read only qgrid instance for interactively viewing the
        database
        """
        if self.config['Interactive'] is False:
            raise ValueError("interactivity disabled in config")
        grid_options = {'editable':False}
        self.qgrid_widget = self.make_qgrid(self.database,
                                            show_toolbar=True,
                                            precision=3,
                                            grid_options=grid_options)
        return self.qgrid_widget


    def edit_interactive(self):
        """
        returns an editable qgrid instance for interactively viewing the
        database. Call the method save_interactive to save any changes made
        """
        if self.config['Interactive'] is False:
            raise ValueError("interactivity disabled in config")
        grid_options = {'editable':True}
        self.qgrid_widget = self.make_qgrid(self.database,
                                            show_toolbar=True,
                                            precision=3,
                                            grid_options=grid_options)
        return self.qgrid_widget

    def save_interactive(self):
        """
        saves changes made to the qgrid when interfactive edit mode has been
        used"""
        #dframe = self.qgrid_widget._unfiltered_dframe
        #dframe.remove
        #dframe_new = self.qgrid_widget.get_changed_df()
        self.database = self.qgrid_widget.get_changed_df()

    def get_database(self):
        """returns the pandas data frame"""
        return self.database

    def set_database(self, database):
        """set the pandas data frame"""
        self.database = database

    def save_to_file(self, path=None):
        """save the pandas dataframe to the root path of the database
        file structure"""
        if path is None:
            path = self.base_path
        self.database.to_csv(os.path.join(path, "database.csv"),
                             index=False, index_label='Index')

    def register_alias(self, row_id, alias):
        """create an alias for a material to easily access it from the
        database"""
        index = None
        if isinstance(row_id, pd.core.series.Series):
            index = row_id.Index
        elif isinstance(row_id, int):
            index = row_id
        if index is None:
            raise ValueError("row_id: {}".format(row_id) +
                             " with type {}".format(type(row_id)) +
                             " not understood")
        self.database.at[index, 'Alias'] = alias

    def get_material(self, identifier):
        """get a material from the database using its alias"""
        if isinstance(identifier, str):
            row = self.database.loc[self.database.Alias == identifier, :]            
        else:
            raise ValueError("identifier must be of type str")
        file_path = os.path.join(self.base_path,
                                 row.Database.values[0], row.Path.values[0])
        mat = MaterialData(file_path=file_path,
                           spectrum_type=row.SpectrumType.values[0],
                           unit=row.Unit.values[0])
        return mat

    def make_reference_spectrum(self, config):
        """make the spectrum with which every material in the database will
        be evaluated"""
        val = config['ReferenceSpectrum']['Value']
        spec_type = config['ReferenceSpectrum']['SpectrumType']
        unit = config['ReferenceSpectrum']['Unit']
        self.reference_spectrum = Spectrum(val, spectrum_type=spec_type,
                                           unit=unit)


    def read_refractive_index_info_db(self, db_path):
        """read the file structure provided by the refractiveindex.info
        website"""
        with codecs.open(os.path.join(db_path, "library.yml"),
                         'r', encoding='utf8') as stream:
            data = YAML(typ='safe').load(stream)
            dframe = pd.DataFrame(columns=MaterialDatabase.META_DATA.keys())
            database_list = []
            database_list = self._read_ri_info_shelves(data,
                                                       db_path,
                                                       database_list)

            """
            for shelf_data in data:
                #shelf = shelf_data['SHELF']
                content = shelf_data['content']
                for shelf_content in content:
                    if "DIVIDER" in shelf_content.keys():
                        #shelf_divider = shelf_content['DIVIDER']
                        continue
                    if "BOOK" in shelf_content.keys():
                        #book = shelf_content['BOOK']
                        #full_name = shelf_content['name']
                        for book_content in shelf_content['content']:
                            if "DIVIDER" in book_content:
                                continue
                            #page = book_content['PAGE']
                            #data_set_name = book_content['name']
                            #path = book_content['data']
                            full_file = os.path.join(db_path,
                                                     'data',
                                                     book_content['data'])
                            mat = MaterialData(file_path=full_file,
                                               spectrum_type='wavelength',
                                               unit='micrometer')
                            content_dict = {"Alias":"",
                                            "Name":shelf_content['BOOK'],
                                            "FullName":shelf_content['name'],
                                            "Author":book_content['PAGE'],
                                            "Path":book_content['data'],
                                            "Database":"RefractiveIndexInfo"}
                            content_dict['SpectrumType'] = 'wavelength'
                            content_dict['Unit'] = 'micrometer'
                            valid_range = mat.get_maximum_valid_range()
                            content_dict['SpectrumLowerBound'] = valid_range[0]
                            content_dict['SpectrumUpperBound'] = valid_range[1]
                            meta_data = mat.meta_data
                            content_dict['Reference'] = meta_data['Reference']
                            content_dict['Comment'] = meta_data['Comment']
                            try:
                                ref_spectrum = self.reference_spectrum
                                ref_index = mat.getNKData(ref_spectrum)
                            except ValueError:
                                ref_index = np.nan + 1j* np.nan


                            content_dict['N_Reference'] = np.real(ref_index)
                            content_dict['K_Reference'] = np.imag(ref_index)
                            database_list.append(content_dict)
            """
        dframe = pd.DataFrame(database_list,
                              columns=MaterialDatabase.META_DATA.keys())
        return dframe

    def _read_ri_info_shelves(self, data, db_path, database_list):
        for shelf_data in data:
            #shelf = shelf_data['SHELF']
            content = shelf_data['content']
            for shelf_content in content:
                if "DIVIDER" in shelf_content.keys():
                    #shelf_divider = shelf_content['DIVIDER']
                    continue
                if "BOOK" in shelf_content.keys():
                    shelf = shelf_content
                    book = shelf_content['content']
                    database_list = self._read_ri_info_book(db_path,
                                                            shelf,
                                                            book,
                                                            database_list)
        return database_list

    def _read_ri_info_book(self, db_path, shelf, book, database_list):
        for book_content in book:
            if "DIVIDER" in book_content:
                continue
            #page = book_content['PAGE']
            #data_set_name = book_content['name']
            #path = book_content['data']
            full_file = os.path.join(db_path,
                                     'data',
                                     book_content['data'])
            mat = MaterialData(file_path=full_file,
                               spectrum_type='wavelength',
                               unit='micrometer')
            content_dict = {"Alias":"",
                            "Name":shelf['BOOK'],
                            "FullName":shelf['name'],
                            "Author":book['PAGE'],
                            "Path":book['data'],
                            "Database":"RefractiveIndexInfo"}
            content_dict['SpectrumType'] = 'wavelength'
            content_dict['Unit'] = 'micrometer'
            valid_range = mat.get_maximum_valid_range()
            content_dict['SpectrumLowerBound'] = valid_range[0]
            content_dict['SpectrumUpperBound'] = valid_range[1]
            content_dict['Reference'] = mat.meta_data['Reference']
            content_dict['Comment'] = mat.meta_data['Comment']
            try:
                ref_spectrum = self.reference_spectrum
                ref_index = mat.getNKData(ref_spectrum)
            except ValueError:
                ref_index = np.nan + 1j* np.nan

            content_dict['N_Reference'] = np.real(ref_index)
            content_dict['K_Reference'] = np.imag(ref_index)
            database_list.append(content_dict)
        return database_list



    def read_filmmetrics_db(self, db_path):
        """read the file structure provided my filmetrics.com"""
        return self._read_text_db(db_path, "Filmetrics")

    def read_user_data_db(self, db_path):
        """read user data files"""
        return self._read_text_db(db_path, "UserData")


    def _read_text_db(self, db_path, database_name):
        """internal function used to load all txt or csv files in a folder"""
        onlyfiles = [f for f in os.listdir(db_path)
                     if os.path.isfile(os.path.join(db_path, f))]

        dframe = pd.DataFrame(columns=MaterialDatabase.META_DATA.keys())
        database_list = []
        for filename in onlyfiles:
            [name, ext] = os.path.splitext(filename)
            allowed_ext = {'.txt', '.csv'}
            if ext not in allowed_ext:
                continue

            mat = MaterialData(file_path=os.path.join(db_path, filename),
                               spectrum_type='wavelength',
                               unit='nanometer')

            content_dict = {}
            content_dict['Alias'] = ""
            content_dict['Name'] = name
            content_dict['FullName'] = mat.meta_data['FullName']
            content_dict['Author'] = mat.meta_data['Author']
            content_dict['Database'] = database_name
            content_dict['Comment'] = mat.meta_data['Comment']
            content_dict['Reference'] = mat.meta_data['Reference']
            content_dict['SpectrumType'] = "wavelength"
            content_dict['Unit'] = 'nanometer'
            valid_range = mat.get_maximum_valid_range()
            content_dict['SpectrumLowerBound'] = valid_range[0]
            content_dict['SpectrumUpperBound'] = valid_range[1]
            content_dict['Path'] = filename
            try:
                ref_index = mat.getNKData(self.reference_spectrum)
            except ValueError:
                ref_index = float('nan') + 1j* float('nan')

            content_dict['N_Reference'] = np.real(ref_index)
            content_dict['K_Reference'] = np.imag(ref_index)
            database_list.append(content_dict)
        dframe = pd.DataFrame(database_list,
                              columns=MaterialDatabase.META_DATA.keys())
        return dframe




if __name__ == "__main__":
    pass
