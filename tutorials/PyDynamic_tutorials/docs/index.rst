.. PyDynamic_tutorials' documentation master file, which we copied heavily from the
   docs of https://github.com/cornellius-gp/gpytorch, because we liked so
   much the way they presented their tutorials, examples and actual
   documentation of the code side by side.

:github_url: https://github.com/PTB-M4D/PyDynamic_tutorials

PyDynamic_tutorials - Assistance in understanding uncertainty propagation with PyDynamic
========================================================================================

*PyDynamic_tutorials* is a collection of tutorials based on Jupyter notebooks which are
designed to simplify the handling of PyDynamic. The tutorials range from introductory
examples to more in-depth use cases in the context of `our work at PTB <https://www
.ptb.de/cms/en/ptb/ptb-management/pstab/pst-1-coordination-digitalization.html>`_.

For the *PyDynamic_tutorials* homepage go to
`GitHub <https://github.com/PTB-M4D/PyDynamic_tutorials>`_.

*PyDynamic_tutorials* are written in Python 3.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   Get going with the tutorials <README>

.. toctree::
   :numbered: 1
   :maxdepth: 1
   :caption: Deconvolution tutorial

   PyDynamic_tutorials/deconvolution/01 Basic measurement data pre-processing.ipynb
   PyDynamic_tutorials/deconvolution/02 Preparation of calibration data.ipynb
   PyDynamic_tutorials/deconvolution/03 Interpolation and extrapolation of calibration data.ipynb
   PyDynamic_tutorials/deconvolution/04 Calculation of impulse response of hydrophone.ipynb
   PyDynamic_tutorials/deconvolution/05 Deconvolution in the frequency domain.ipynb
   PyDynamic_tutorials/deconvolution/06 Regularized deconvolution.ipynb

.. toctree::
   :maxdepth: 1
   :caption: Uncertainty tutorial

   PyDynamic_tutorials/uncertainty/01 Basic measurement data pre-processing.ipynb
   PyDynamic_tutorials/uncertainty/02 Basic interpolation.ipynb
   PyDynamic_tutorials/uncertainty/03 Basic extrapolation.ipynb

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
