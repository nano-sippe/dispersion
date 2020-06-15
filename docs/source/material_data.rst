The MaterialData Class
======================
This class defines the optical parameters for a given material. The optical
parameters are defined via the complex refractive index or equivalently the
complex permittivity. As a shorthand, we will refer to the real part of the
refractive index as n, the imaginary part as k and the complex refractive index
as nk. Similarly, the shorthand for permittivity is eps_r, eps_i and eps

 There are
multiple ways to initalise this class. Typically the objects of this class
will be generated using the material database.

It can also be initalised in the following ways,

- using the path to a file
- using a constant value for n, nk, eps_r or eps.
- using tabulated data for n, nk or eps
- using a predefined model

Apart from the file path, these different definitions can be mixed and matched.
For example a model or tabulated data for n, while taking a constant value for
k.

A material is full defined when either both the real and imaginary parts of the
refractive index or permittivity are defined, or alternatively a complex
value for either refractive index or permittivity is defined.

Once a material has been fully defined, the refractive index or permittivity can
be evaluated on a given spectrum. The spectrum can be wavelength, frequency,
angular frequency or energy. For more information see Spectrum

::
    import numpy as np
    from refractive_index_database.material_data import MaterialData
    from refractive_index_database.spectrum import Spectrum
    mat = MaterialData(fixed_n = 1.5) # k will be set = 0
    spm = Spectrum( np.arange(380, 750, 10 ),
                   spectrum_type= 'Wavelength',
                   unit = 'nanometer')
    nk_values = mat.get_nk_data(spm)
    eps = mat.get_permittivity(spm)


Interpolation
=============
If tabulated data is used to initalise the MaterialData, it will be
automatically interpolated. The order of interpolation can be set by passing
interp_order as a keyword to the MaterialData constructor. The order must be an
integer. The default value is 1 (linear interpolation).

Extrapolation
=============
Data can be extrapolated outside of the range in which it is defined. This
should be done with great care, as extrapolated values may not even be
qualitatively correct. However in circumstances where the material dispersion is
very low, it may be practical to extrapolate the close to the spectrum of known
values. Note that since the real and imaginary parts are extrapolated separately
they must be independent of one another. Therefore, the material must be defined
via separate real and imaginary parts, rather than via a complex value.

Extrapolation is achieved as follows,

::
    new_spectrum = Spectrum( 800., spectrum_type='Wavelength', unit='nm')
    mat.extrapolate(new_spectrum, spline_order=2)

Due to extrapolation using splines, the results can vary greatly depending on
the spline order used. For this reason it is recommended to verify the results
of extrapolation before using the results for further calculations.
