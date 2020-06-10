"""provides functions for reading and writing the configuration file."""
#import sys
import os
from warnings import warn
from refractive_index_database.io import (read_yaml_file, read_yaml_string,
                                          write_yaml_file)
if os.name == 'nt':
    PLATFORM = "Windows"
elif os.name == 'posix':
    PLATFORM = 'Linux'
else:
    raise OSError("curret os type could not be determined."+
                  " Configuration file location unknown.")

def default_config():
    """provides default values for the configuration.

    Returns
    -------
    dict or OrderedDict
        the tree of configuration data
    """
    yaml_str = """\
    Path: /path/to/database/file/structure
    Interactive: true #for jupyter interfactive editing
    Modules: # which databases to include
      UserData: true
      RefractiveIndexInfo: true
      Filmetrics: true
    ReferenceSpectrum: # evaluate n and k at given spectral value
      Value: 632.8
      SpectrumType: wavelength
      Unit: nanometer
    """
    config = read_yaml_string(yaml_str)
    return config

def _get_config_dir():
    if PLATFORM == 'Windows':
        user_dir = os.environ["LOCALAPPDATA"]
        config_dir = os.path.join(user_dir, "refractive_index_database")
    elif PLATFORM == 'Linux':
        home_dir = os.environ["HOME"]
        config_dir = os.path.join(home_dir, ".config",
                                  "refractive_index_database")
    return config_dir


def write_config(config):
    """write the configuration data to file.

    Parameters
    ----------
    config: dict or OrderedDict
        the configuration data

    Warnings
    --------
    No check is made if the config is valid or complete.
    """
    dir_path = _get_config_dir()
    file_path = os.path.join(dir_path, 'config.yaml')
    write_yaml_file(file_path, config)

def read_config():
    """read the configuration data from file.

    Returns
    -------
    dict or OrderedDict
        the configuration data
    """
    dir_path = _get_config_dir()
    file_path = os.path.join(dir_path, 'config.yaml')
    config = read_yaml_file(file_path)
    return config

def get_config():
    """get the configuration data.

    attempt to read the configuration from file, if not found then return
    default values.

    Returns
    -------
    dict or OrderedDict
        the configuration data
    """
    try:
        config = read_config()
    except OSError as exc:
        warn("No configuration file found, generating default config.")
        config = default_config()
    return config

if __name__ == "__main__":
    print(get_config())
