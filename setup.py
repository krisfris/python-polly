import site
import sys
from setuptools import setup, find_packages


# Workaround to install in user dir but editable,
# see https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='python-polly',
    version='0.1.0',
    description='Wrapper for AWS Polly with segmentation, playback queue and client-server setup',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/krisfris/python-polly',
    author='Kris',
    author_email='31852063+krisfris@users.noreply.github.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests', 'click'
    ],
    extras_require={
        'server': ['appdirs', 'pyaudio', 'nltk', 'boto3', 'werkzeug',
                   'json-rpc', 'pyqt5']
    },
    entry_points='''
        [console_scripts]
        polly=polly.cli:cli
    ''',
)
