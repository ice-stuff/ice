import os
from setuptools import setup, find_packages

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
        os.path.join(os.path.dirname(__file__), 'bin', 'ice-shell')
    ],

    # Dependencies
    install_requires=[
        "eve>=0.4",
        "IPython>=2.3.0",
        "requests>=1.2.0",
        "fabric>=1.10.0"
    ]
)
