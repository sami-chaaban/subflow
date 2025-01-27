from distutils.core import setup
from setuptools import find_packages
import subflow

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='subflow',
      version=subflow.__version__,
      description='Pipeline for subtracting filaments from cryo-EM micrographs.',
      author='Sami Chaaban',
      author_email='chaaban@mrc-lmb.cam.ac.uk',
      url='http://pypi.python.org/pypi/subflow/',
      #long_description=long_description,
      #long_description_content_type='text/markdown',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          "console_scripts": [
            "subflow = subflow.__main__:main",
            ],
      },
      install_requires=["pandas", "starparser", "starfile", "sv_ttk", "mrcfile", "numpy", "scipy", "cryosparc-tools~=4.6.0"],
      python_requires='>=3.9',
      license='MIT'
     )
