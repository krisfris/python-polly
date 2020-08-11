import site
import sys
from setuptools import setup, find_packages


# Workaround to install in user dir but editable,
# see https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]


setup(
    name='python-polly',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests', 'click'
    ],
    extras_require={
        'core': ['appdirs', 'pyaudio', 'nltk', 'boto3', 'werkzeug',
                 'json-rpc'],
        'gui': ['pyqt5'],
    },
    entry_points='''
        [console_scripts]
        polly=polly.cli:cli
    ''',
)
