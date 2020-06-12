#from git import Repo
import argparse
import os
from refractive_index_database.config import default_config
def getParser():
    parser = argparse.ArgumentParser(description='clone the rerfactive index '\
                                     'info database')
    parser.add_argument('--install_dir', default=None, type=str)
    return parser

def get_root_dir(conf):
    valid_input = False
    while not valid_input:
        database_dir = input("path for root directory of the database file" +
                            " system [default: {}]> ".format(conf['Path']))
        if database_dir == "":
            database_dir = conf['Path']
        if os.path.isabs(database_dir):
            valid_input = True
        else:
            print("input is not a valid path")
    confirmed_input = False
    while not confirmed_input:
        confirmation1 = input("confirm root directory as "+
                              "{} [y/n]> ".format(database_dir))
        if confirmation1 in {'y','yes'}:
            confirmed_input = True
        elif confirmation1 in {'n','no'}:
            confirmed_input = False
            break
        else:
            print("input invalid")
    return [database_dir, confirmed_input]


def setup():
    conf = default_config()
    print("This script will provide a default configuration for the \n"+
           "refractive index database package")
    confirmed_valid_path = False
    while not confirmed_valid_path:
        [path, confirmed_valid_path] = get_root_dir(conf)
    print(path)


if __name__ == "__main__":
    setup()
    #args = getParser().parse_args()
    #git_url = "https://github.com/polyanskiy/refractiveindex.info-database.git"
    #Repo.clone_from(git_url, args.install_dir)
