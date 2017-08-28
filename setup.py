
from setuptools import find_packages, setup

setup(
    name='bi-redirect',
    version='0.0.1',
    url='https://github.com/chukysoria/biredirect',
    license='Apache License, Version 2.0',
    author='chukysoria',
    author_email='nomail@nomail.com',
    description='Bi-BOX redirector',
    long_description='None',
    keywords='redirector',
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite="tests",
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'boxsdk >= 1.5.4',
        'bs4 >=0.0.1',
        'Flask >=0.12.2',
        'gunicorn == 19.6.0',
        'invoke >= 0.20.4',
        'python-dotenv >=0.6.5',
        'redis >=2.10.6',
        'requests >=2.18.3'],
    entry_points={
        'console_scripts': [
            'spotifyconnect = biredirect.redirector'
        ]
    }
)
