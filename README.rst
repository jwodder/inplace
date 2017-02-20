.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active - The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://travis-ci.org/jwodder/inplace.svg?branch=master
    :target: https://travis-ci.org/jwodder/inplace

.. image:: https://coveralls.io/repos/github/jwodder/inplace/badge.svg?branch=master
    :target: https://coveralls.io/github/jwodder/inplace?branch=master

.. image:: https://img.shields.io/pypi/pyversions/in_place.svg
    :target: https://pypi.python.org/pypi/in_place

.. image:: https://img.shields.io/github/license/jwodder/inplace.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/inplace>`_
| `PyPI <https://pypi.python.org/pypi/in_place>`_
| `Issues <https://github.com/jwodder/inplace/issues>`_

The ``in_place`` module provides Python classes for reading & writing a file
"in-place": data that you write ends up at the same filepath that you read
from, and ``in_place`` takes care of all the necessary mucking about with
temporary files for you.

For example, given the file ``somefile.txt``::

    'Twas brillig, and the slithy toves
        Did gyre and gimble in the wabe;
    All mimsy were the borogoves,
        And the mome raths outgrabe.

and the program ``disemvowel.py``::

    import in_place

    with in_place.InPlace('somefile.txt') as fp:
        for line in fp:
            fp.write(''.join(c for c in line if c not in 'AEIOUaeiou'))

after running the program, ``somefile.txt`` will have been edited in place,
reducing it to just::

    'Tws brllg, nd th slthy tvs
        Dd gyr nd gmbl n th wb;
    ll mmsy wr th brgvs,
        nd th mm rths tgrb.

and no sign of those pesky vowels remains!  If you want a sign of those pesky
vowels to remain, you can instead save the file's original contents in, say,
``somefile.txt~`` by constructing the filehandle with::

    in_place.InPlace('somefile.txt', backup_ext='~')

or save to ``someotherfile.txt`` with::

    in_place.InPlace('somefile.txt', backup='someotherfile.txt')

Compared to the in-place filtering implemented by the Python standard library's
|fileinput|_ module, ``in_place`` offers the following benefits:

- Instead of hijacking ``sys.stdout``, a new filehandle is returned for
  writing.
- The filehandle supports all of the standard I/O methods, not just
  ``readline()``.
- There are options for setting the encoding, encoding error handling, and
  newline policy for opening the file, along with support for opening files in
  binary mode, and these options apply to both input and output.
- The complete filename of the backup file can be specified; you aren't
  constrained to just adding an extension.
- When used as a context manager, ``in_place`` will restore the original file
  if an exception occurs.
- The creation of temporary files won't silently clobber innocent bystander
  files.

.. |fileinput| replace:: ``fileinput``
.. _fileinput: https://docs.python.org/3/library/fileinput.html


Installation
============
Just use `pip <https://pip.pypa.io>`_ (You have pip, right?) to install
``in_place`` and its dependencies::

    pip install in_place


Basic Usage
===========
``in_place`` provides three classes:

- ``InPlaceText``, for working with text files (reading & writing ``unicode``
  objects in Python 2, ``str`` objects in Python 3)

- ``InPlaceBytes``, for working with binary files (reading & writing ``str``
  objects in Python 2, ``bytes`` objects in Python 3)

- ``InPlace``, for just calling ``open()`` and reading & writing whatever the
  current Python's ``str`` type is

All of the classes' constructors take the following arguments:

``name=<PATH>`` (required)
   The path to the file to open & edit in-place

``backup=<PATH>``
   If set, the original contents of the file will be saved to the given path
   when the instance is closed.

``backup_ext=<EXTENSION>``
   If set, the path to the backup file will be created by appending
   ``backup_ext`` to the original file path.

   ``backup`` and ``backup_ext`` are mutually exclusive.  ``backup_ext`` cannot
   be set to the empty string.

``delay_open=<BOOL>``
   By default, the instance is opened (including creating temporary files and
   so forth) as soon as it's created.  Setting ``delay_open=True`` disables
   this; the instance must then be opened either via the ``open()`` method or
   by using it as a context manager.

``move_first=<BOOL>``
   If ``True``, move the input file to a temporary location first and create
   the output file in its place (à la ``fileinput``) rather than the default
   behavior of creating the output file at a temporary location and only moving
   things around once ``close()`` is called (à la GNU ``sed(1)``).

The ``InPlaceText`` constructor additionally accepts the optional arguments
``encoding``, ``errors``, and ``newline``, which are passed straight through to
``io.open`` for both reading and writing.

Once open, ``in_place`` instances act as filehandles with the usual filehandle
attributes, specifically::

    __iter__()              close()                 closed
    flush()                 name                    read()
    readall() *             readinto() *            readline()
    readlines()             write()                 writelines()

    * InPlaceBytes only

The classes also feature the following new or modified attributes:

``open()``
   Open the instance, creating filehandles for reading & writing.  This method
   must be called first before any of the other I/O methods can be used.  It is
   normally called automatically upon instance initialization unless
   ``delay_open`` was set to ``True``.  A ``ValueError`` is raised if this
   method is called more than once in an instance's lifetime.

``close()``
   Close filehandles and move files to their final destinations.  If called
   after the filhandle has already been closed, ``close()`` does nothing.

   Be sure to always close your instances when you're done with them by calling
   ``close()`` or ``rollback()`` either explicity or implicitly (i.e., via use
   as a context manager).

``rollback()``
   Like ``close()``, but discard the output data (keeping the original file
   intact) instead of replacing the original file with it

``__enter__()``, ``__exit__()``
   When an ``in_place`` instance is used as a context manager, it will be
   opened (if not open already) on entering and either closed (if all went
   well) or rolled back (if an exception occurred) on exiting.  ``in_place``
   context managers are not `reusable`_ but are `reentrant`_ (as long as no
   further operations are performed after the innermost context ends).

``input``
   The actual filehandle that data is read from, in case you need to access it
   directly

``output``
   The actual filehandle that data is written to, in case you need to access it
   directly

.. _reentrant: https://docs.python.org/3/library/contextlib.html#reentrant-cms
.. _reusable: https://docs.python.org/3/library/contextlib.html#reusable-context-managers
