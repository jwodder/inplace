from   os.path    import dirname, join
import re
from   setuptools import setup

with open(join(dirname(__file__), 'inplace.py')) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError('Unable to find own __version__ string')

###with open(join(dirname(__file__), 'README.rst')) as fp:
###    long_desc = fp.read()

setup(
    name='inplace',
    version=version,
    py_modules=['inplace'],
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='inplace@varonathe.org',
    ###keywords='',
    ###description='',
    ###long_description=long_desc,
    url='https://github.com/jwodder/inplace',

    setup_requires=['pytest-runner>=2.0,<3'],
    install_requires=[],
    tests_require=['pytest>=2.8,<3'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'License :: OSI Approved :: MIT License',

        ###
    ],
)
