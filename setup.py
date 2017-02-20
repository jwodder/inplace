from   os.path    import dirname, join
import re
from   setuptools import setup

with open(join(dirname(__file__), 'in_place.py')) as fp:
    for line in fp:
        m = re.search(r'^\s*__version__\s*=\s*([\'"])([^\'"]+)\1\s*$', line)
        if m:
            version = m.group(2)
            break
    else:
        raise RuntimeError('Unable to find own __version__ string')

with open(join(dirname(__file__), 'README.rst')) as fp:
    long_desc = fp.read()

setup(
    name='in_place',
    version=version,
    py_modules=['in_place'],
    license='MIT',
    author='John Thorvald Wodder II',
    author_email='inplace@varonathe.org',
    keywords='inplace in-place io open file tmpfile tempfile sed redirection',
    description='In-place file processing',
    long_description=long_desc,
    url='https://github.com/jwodder/inplace',

    install_requires=['six>=1.4,<2'],

    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: System :: Filesystems',
        'Topic :: Text Processing :: Filters',
    ],
)
