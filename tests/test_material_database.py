import pytest
import numpy as np
from refractive_index_database.material_database import MaterialDatabase
from refractive_index_database.config import get_config

config = get_config()

def test_mdb_init():
    mdb = MaterialDatabase(config)

def test_get_mat():
    mdb = MaterialDatabase(config)

if __name__ == "__main__":
    test_mdb_init()
    
