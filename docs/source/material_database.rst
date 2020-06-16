The MaterialDatabase Class
==========================
This page describes the basic usage of the ``MaterialDatabase`` class. This class
is used for interfacing with the database file. The database file is a catalogue
telling python where to find the data files to create instances of
``MaterialData``. To open the database in python use,

::
   
  from refractive_index_database import MaterialDatabase
  mdb = MaterialDatabase()

The database file system looks like this,

::
   
  database_root/
      database.csv
      UserData/
          userfile1.txt
          userfile2.yml
          ...
      Module1/
          Module1_subdir1/
              mat1.yml
              mat2.yml
          Module1_subdir2/
              anothermat.yml
          ...
      Module2/
      ...

The database file itself (filename configurable), sits at the
root level of the database filesystem in the database_root directory
(configurable). The other folders present in the root directory are the
installed modules. By default a module called UserData is installed for the
user to keep their data. Other modules consist of literature material databases
available for download. See modules for a list of supported modules.

Building the Database
---------------------
Whenever new files are added to the database file system, the database needs to
be rebuilt.

To build the database you can use the script included in this package

::
   
  > rebuild_material_database --modules All

or alternatively you can rebuild from inside python

::
   
  from refractive_index_database import MaterialDatabase
  mdb = MaterialDatabase(rebuild='All')

When rebuilding the database, you can choose to rebuild either some or all of
the modules.

Setting an Alias
----------------
Many materials have different data files associated with them. In order to
uniquely identify materials in the database, a unique alias can be assigned to
each material. This alias will be used later to extract the material from the
database. By default all materials do not have any alias defined.

In order to set an alias, the database file needs to be edited. This can be done
in three ways: Externally, using python or interactively using iPython with the
qgrid extension.

The following shows how to edit an alias using python.

::
   
    row = mdb.database[(mdb.database.Name == name)]
    mdb.register_alias(row, "alias")

This will not work if there are multiple materials in the database with the same
"Name" attribute. In order to set the alias in this case, either use the path
to the file on the inside the module folder as the filter,

::
   
    row = mdb.database[(mdb.database.Path == path/to/file.txt)]
    mdb.register_alias(row, "alias")
    mdb.save_to_file()

or use the interactive editing. For this the qgrid IPython extension needs to be
installed. After installation, open the database in an IPython like environment
(such as a jupyter notebook) and use,

::
   
  mdb.edit_interactive()

note that "Interactive" must be set to true in the package configuration file
to use interactive editing. After the aliases have been set in the alias column
for the appropriate materials, the database must be saved via,

::
   
  mdb.save_interactive()
  mdb.save_to_file()


Accessing the Database
----------------------
To get a material from the database simply use

::
   
  mat = mdb.get_material("<mat_alias>")

this returns a MaterialData object. If the argument of get_material is a string,
then it must refer to the alias of the material in the database. If the
argument is an integer, it refers to the row number in the database.
