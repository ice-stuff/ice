import os
from setuptools import setup, find_packages

# Path defs
base_path = os.path.dirname(__file__)

# Register setup
setup(
    # Metadata
    name="iCE",
    version="0.0.1",
    author="George Lestaris",
    author_email="glestaris@gmail.com",
    description="Interactive cloud experiments and monitoring",

    # Packages
    packages=find_packages(),
    # zip_safe=False,                     # does not produce the EGG file
    scripts=[
        os.path.join(base_path, 'bin', 'ice-shell')
    ],

    # Dependencies
    install_requires=[
        "eve>=0.4",
        "IPython>=2.3.0"
    ]
)
