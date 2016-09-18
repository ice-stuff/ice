import os
import setuptools

setuptools.setup(
    # Metadata
    name="iCE",
    version="2.0.0",
    author="George Lestaris",
    author_email="glestaris@gmail.com",
    description="Interactive cloud experiments and monitoring",

    # Packages
    packages=setuptools.find_packages(exclude=['test']),
    scripts=[
        os.path.join(os.path.dirname(__file__), 'bin', 'ice-shell'),
        os.path.join(os.path.dirname(__file__), 'bin', 'ice-server')
    ],

    # Dependencies
    install_requires=[
        "eve>=0.6.4",
        "fabric>=1.12.0",
        "boto>=2.42.0",
        "IPython>=5.1.0",
        "requests>=2.11.0"
    ],

    # Configuration
    data_files=[
        (
            'etc/ice', [
                'config/default/ice.ini',
                'config/default/logging.ini'
            ]
        )
    ]
)
