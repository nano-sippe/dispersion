from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="dispersion", # Replace with your own username
    version="0.1.0-beta.5",
    author="Phillip Manley",
    author_email="phillip.manley@helmholtz-berlin.de",
    description="support for libraries of optical dispersion (refractive index) data files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nano-sippe/dispersion",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['numpy', 'matplotlib', 'pandas', 'scipy', 'PyYAML'],
    python_requires='>=3.6',
    include_package_data=True,
    entry_points={
        'console_scripts': ['dispersion_setup='+
                            'dispersion.scripts.'+
                            'setup_dispersion:main',
                            'dispersion_catalogue_rebuild='+
                            'dispersion.scripts.'+
                            'catalogue_rebuild:main',],
    }
)

#data_files=[('config',['cfg/config.yaml'])],
