from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="refractive_index_database", # Replace with your own username
    version="0.0.1",
    author="Phillip Manley",
    author_email="phillip.manley@helmholtz-berlin.de",
    description="database for refractive index data files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nano-sippe/refractive_index_database",
    packages=setuptools.find_packages(where="src"),
    package_dir = {"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy','matplotlib','pandas','ruamel.yaml'],
    python_requires='>=3.6',
    package_data = {'refractive_index_database':['config.yaml']},
    include_package_data=True,
)

#data_files=[('config',['cfg/config.yaml'])],
