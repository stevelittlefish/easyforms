import sys
from setuptools import setup

if sys.version_info.major < 3:
    sys.exit('Sorry, this library only supports Python 3')

setup(
    name='easyforms',
    packages=['easyforms'],
    include_package_data=True,
    version='0.1.5',
    description='Form processing library for Flask and Jinja2',
    author='Stephen Brown (Little Fish Solutions LTD)',
    author_email='opensource@littlefish.solutions',
    url='https://github.com/stevelittlefish/easyforms',
    download_url='https://github.com/stevelittlefish/easyforms/archive/v0.1.5.tar.gz',
    keywords=['flask', 'forms', 'jinja2', 'easy'],
    license='Apache',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Flask',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'littlefish>=0.0.3',
        'Flask>=0.12.0',
        'Jinja2>=2.9.0',
        'requests>=2.18.3'
    ],
)

