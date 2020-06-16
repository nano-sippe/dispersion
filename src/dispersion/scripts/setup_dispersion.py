#!/usr/bin/env python
"""
setup the disperion database file structure and configuration file
"""
import os
import tempfile
from dispersion import default_config


def get_root_dir(conf):
    """
    get the root dir from the user
    """
    question = ("path for root directory of the catalogue file" +
                " system [default: {}]> ")
    default = conf['Path']
    validator = os.path.isabs
    data_name = "root directory"
    return ask_and_confirm(question, default, validator, data_name)

def get_catalogue_name(conf):
    """
    get the catalogue file name from the user
    """
    question = ("name of the catalogue file" +
                " [default: {}]> ")
    default = conf['File']
    validator = valid_file_name
    data_name = "catalogue file name"
    return ask_and_confirm(question, default, validator, data_name)

def ask_and_confirm(question, default, validator, data_name, confirm=True):
    """
    Returns
    -------
    user_input: str
        the data from the user
    confirmed_input: bool
        true if the input was confirmed by the user

    Parameters
    ----------
    question: str
        the question to prompt the user input
    default: str
        the default value of this value
    validator: function
        function to validate the input
    data_name: str
        name of the data that is being input
    """
    user_input = ask(question, default, validator)
    confirmation_question = ("confirm {} as ".format(data_name) +
                             "{}? [y/n]> ".format(user_input))
    return [user_input, get_confirmation(confirmation_question)]


def ask(question, default, validator):
    """
    ask for user input with default value and then validate
    """
    valid_input = False
    while not valid_input:
        user_input = input(question.format(default))
        if user_input == "":
            user_input = default
        if validator(user_input):
            valid_input = True
        else:
            print("input is not valid")
    return user_input

def get_confirmation(question):
    """
    get a yes/no answer to a question
    """
    confirmed_input = False
    while not confirmed_input:
        confirmation1 = input(question)
        if confirmation1 in {'y', 'yes'}:
            confirmed_input = True
        elif confirmation1 in {'n', 'no'}:
            confirmed_input = False
            break
        else:
            print("input invalid")
    return confirmed_input

def valid_file_name(filename):
    """
    test if filename is valid

    create a file with the filename in a temporary directory and delete the
    directory afterwards.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            open(filename, 'r')
            return True
        except IOError:
            try:
                open(filename, 'w')
                return True
            except IOError:
                return False

def install_modules(conf):
    """
    make a subfolder for each module and ask to download files
    """
    for module in conf['Modules']:
        if conf['Modules'][module]:
            module_dir = os.path.join(conf['Path'], module)
            if not os.path.isdir(module_dir):
                os.mkdir(module_dir)
            if module == "RefractiveIndexInfo":
                install_rii(conf)

def install_rii(conf):
    """
    download the refractive index info database from github
    """
    question = ("download the refractive index info database from github?" +
                " (required python package <git>)" +
                " [y/n]> ")
    install = get_confirmation(question)
    if install:
        from git import Repo
        git_url = "https://github.com/polyanskiy/refractiveindex.info-database.git"
        install_dir = os.path.join(conf['Path'], "RefractiveIndexInfo")
        Repo.clone_from(git_url, install_dir)


def main():
    conf = default_config()
    print("This script will provide a default configuration for the \n"+
          "dispersion package")
    confirmed_valid_path = False
    while not confirmed_valid_path:
        [path, confirmed_valid_path] = get_root_dir(conf)
    conf['Path'] = path
    #print("Path will be se to: {}".format(path))
    confirmed_db_nane = False
    while not confirmed_db_nane:
        [name, confirmed_db_nane] = get_catalogue_name(conf)
    conf['File'] = name
    #print("Filename will be set to {}".format(name))
    install_modules(conf)



if __name__ == "__main__":
    main()
