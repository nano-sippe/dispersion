# config.py
import sys
import os
try:
    from ruamel.yaml import YAML
except ModuleNotFoundError as e:
    from ruamel_yaml import YAML

def default_config():
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
    yaml = YAML()
    config = yaml.load(yaml_str)
    return config

def write_config(config):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path,'config.yaml')
    with open(file_path,'w') as fp:
        yaml = YAML()
        yaml.dump(config,fp)

def read_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path,'config.yaml')
    if os.path.isfile(file_path):
        with open(file_path,'r') as fp:
            yaml = YAML()
            config = yaml.load(fp)
    else:
        config = default_config()
    return config

def get_config():
    config = read_config()
    return config

if __name__ == "__main__":
    print(get_config())
