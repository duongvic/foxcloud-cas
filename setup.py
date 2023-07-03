from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

about = {}
with open(os.path.join(here, 'foxcloud', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name='foxcloud',
    version=os.getenv('BUILD_VERSION', about['__version__']),
    description='Python library for the foxcloud',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='khanhct',
    author_email='trongkhanh.chu@gmail.com',
    url='https://github.com/khanhct/foxcloud',
    packages=find_packages(),
    test_suite='nose.collector',
    install_requires=[
        'python-magnumclient==3.1.0',
        'python-octaviaclient==2.1.0',
        'python-troveclient==5.0.0',
        'python-heatclient==2.2.0',
        # 'boto3==1.14.48',
        'boto3==1.21.23',
        'python-glanceclient==3.2.1',
        'python-neutronclient==7.2.0',
        'python-novaclient==17.2.0',
        'paramiko==2.7.1',
        'python-ldap==3.3.1',
        # 'cryptography==2.9.2',
        'cryptography==3.3.2',
        'pyasn1==0.4.8',
        'urllib3==1.25.11',
        'PyYAML==5.4.1'
    ],
    entry_points={
    })
