from distutils.core import setup
from setuptools import find_packages


setup(
    name='bankdownloads',
    version='0.1',
    author=u'Evan Davey',
    author_email='evan.davey@cochranedavey.com',
    packages=['bankdownloads'],
    scripts=['bin/bankdownload-processor'],
    url='http://github.com/evandavey/bankdownloads',
    license='LICENSE.txt',
    description='Processes and standardises bank transaction downloads',
    long_description=open('README.md').read(),
    install_requires=[
        'mysql-python',
    ],
    data_files=[('etc', ['etc/bankdownloads.conf']),
                
    ],
    zip_safe=False,
)

