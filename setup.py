import setuptools

setuptools.setup(
    # Metadata
    name='iCE',
    version='2.1.0-dev',
    author='George Lestaris',
    author_email='glestaris@gmail.com',
    description='Interactive cloud experiments and monitoring',

    # Packages
    packages=setuptools.find_packages(exclude=['test']),

    # Dependencies
    install_requires=[
        'eve>=0.6.4',
        'fabric>=1.12.0',
        'boto>=2.42.0',
        'requests>=2.11.0',
        'redo>=1.5'
    ]
)
