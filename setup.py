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
    zip_safe=False,                     # does not produce the EGG file

    # Dependencies
    install_requires=[
        "eve>=0.4",
        "IPython>=2.3.0"
    ]
)
