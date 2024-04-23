|repostatus| |ci-status| |coverage| |pyversions| |conda| |license|

.. |repostatus| image:: https://www.repostatus.org/badges/latest/active.svg
    :target: https://www.repostatus.org/#active
    :alt: Project Status: Active - The project has reached a stable, usable
          state and is being actively developed.

.. |ci-status| image:: https://github.com/jwodder/inplace/actions/workflows/test.yml/badge.svg
    :target: https://github.com/jwodder/inplace/actions/workflows/test.yml
    :alt: CI Status

.. |coverage| image:: https://codecov.io/gh/jwodder/inplace/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/inplace

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/in_place.svg
    :target: https://pypi.org/project/in_place

.. |conda| image:: https://img.shields.io/conda/vn/conda-forge/in_place.svg
    :target: https://anaconda.org/conda-forge/in_place
    :alt: Conda Version

.. |license| image:: https://img.shields.io/github/license/jwodder/inplace.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/inplace>`_
| `PyPI <https://pypi.org/project/in_place>`_
| `Issues <https://github.com/jwodder/inplace/issues>`_
| `Changelog <https://github.com/jwodder/inplace/blob/master/CHANGELOG.md>`_

The ``in_place`` module provides an ``InPlace`` class for reading & writing a
file "in-place": data that you write ends up at the same filepath that you read
from, and ``in_place`` takes care of all the necessary mucking about with
temporary files for you.

For example, given the file ``somefile.txt``::

    'Twas brillig, and the slithy toves
        Did gyre and gimble in the wabe;
    All mimsy were the borogoves,
        And the mome raths outgrabe.

and the program ``disemvowel.py``:

.. code:: python

    import in_place

    with in_place.InPlace("somefile.txt") as fp:
        for line in fp:
            fp.write("".join(c for c in line if c not in "AEIOUaeiou"))

after running the program, ``somefile.txt`` will have been edited in place,
reducing it to just::

    'Tws brllg, nd th slthy tvs
        Dd gyr nd gmbl n th wb;
    ll mmsy wr th brgvs,
        nd th mm rths tgrb.

and no sign of those pesky vowels remains!  If you want a sign of those pesky
vowels to remain, you can instead save the file's original contents in, say,
``somefile.txt~`` by constructing the filehandle with:

.. code:: python

    in_place.InPlace("somefile.txt", backup_ext="~")

or save to ``someotherfile.txt`` with:

.. code:: python

    in_place.InPlace("somefile.txt", backup="someotherfile.txt")

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
``in_place`` requires Python 3.8 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install it::

    python3 -m pip install in_place


Basic Usage
===========
``in_place`` provides a single class, ``InPlace``.  Its constructor takes the
following arguments:

``name=<PATH>`` (required)
   The path to the file to open & edit in-place

``mode=<"b"|"t"|None>``
   Whether to operate on the file in binary or text mode.  If ``mode`` is
   ``"b"``, the file will be opened in binary mode, and data will be read &
   written as ``bytes`` objects.  If ``mode`` is ``"t"`` or ``None`` (the
   default), the file will be opened in text mode, and data will be read &
   written as ``str`` objects.

``backup=<PATH>``
   If set, the original contents of the file will be saved to the given path
   when the instance is closed.  ``backup`` cannot be set to the empty string.

``backup_ext=<EXTENSION>``
   If set, the path to the backup file will be created by appending
   ``backup_ext`` to the original file path.

   ``backup`` and ``backup_ext`` are mutually exclusive.  ``backup_ext`` cannot
   be set to the empty string.

``**kwargs``
   Any additional keyword arguments (such as ``encoding``, ``errors``, and
   ``newline``) will be forwarded to ``open()`` when opening both the input and
   output file streams.

``name``, ``backup``, and ``backup_ext`` can be ``str``, filesystem-encoded
``bytes``, or path-like objects.

``InPlace`` instances act as read-write filehandles with the usual filehandle
attributes, specifically::

    __iter__()              __next__()              closed
    flush()                 name                    read()
    read1() *               readinto() *            readinto1() *
    readline()              readlines()             write()
    writelines()

    * binary mode only

``InPlace`` instances also feature the following new or modified attributes:

``close()``
   Close filehandles and move files to their final destinations.  If called
   after the filehandle has already been closed, ``close()`` does nothing.

   Be sure to always close your instances when you're done with them by calling
   ``close()`` or ``rollback()`` either explicitly or implicitly (i.e., via use
   as a context manager).

``rollback()``
   Like ``close()``, but discard the output data (keeping the original file
   intact) instead of replacing the original file with it

``__enter__()``, ``__exit__()``
   When an ``InPlace`` instance is used as a context manager, on exiting the
   context, the instance will be either closed (if all went well) or rolled
   back (if an exception occurred).  ``InPlace`` context managers are not
   reusable_ but are reentrant_ (as long as no further operations are performed
   after the innermost context ends).

``input``
   The actual filehandle that data is read from, in case you need to access it
   directly

``output``
   The actual filehandle that data is written to, in case you need to access it
   directly

.. _reentrant: https://docs.python.org/3/library/contextlib.html#reentrant-cms
.. _reusable: https://docs.python.org/3/library/contextlib.html#reusable-context-managers
