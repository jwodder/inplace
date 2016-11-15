.. image:: http://www.repostatus.org/badges/latest/wip.svg
    :target: http://www.repostatus.org/#wip
    :alt: Project Status: WIP - Initial development is in progress, but there
          has not yet been a stable, usable release suitable for the public.

.. image:: https://travis-ci.org/jwodder/inplace.svg?branch=master
    :target: https://travis-ci.org/jwodder/inplace

..
    .. image:: https://img.shields.io/pypi/pyversions/inplace.svg

.. image:: https://img.shields.io/github/license/jwodder/inplace.svg?maxAge=2592000
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

The ``inplace`` module provides Python classes for reading & writing a file
"in-place": data that you write ends up at the same filepath that you read
from, and ``inplace`` takes care of all the necessary mucking about with
temporary files for you.

For example, given the file ``somefile.txt``::

    'Twas brillig, and the slithy toves
        Did gyre and gimble in the wabe;
    All mimsy were the borogoves,
        And the mome raths outgrabe.

and the program ``disemvowel.py``::

    import inplace

    with inplace.InPlace('somefile.txt') as fp:
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

    inplace.InPlace('somefile.txt', backup_ext='~')

or save to ``someotherfile.txt`` with::

    inplace.InPlace('somefile.txt', backup='someotherfile.txt')

Compared to the in-place filtering implemented by the Python standard library's
|fileinput|_ module, ``inplace`` offers the following benefits:

- ``inplace`` returns a new writable filehandle instead of hijacking
  ``sys.stdout``.
- The returned filehandle supports all of the standard I/O methods, not just
  ``readline()``.
- There are options for setting the encoding, encoding error handling, and
  newline policy for opening the file, along with support for opening files in
  binary mode.
- The complete filename of the backup file can be specified; you aren't
  constrained to just adding an extension.


.. |fileinput| replace:: ``fileinput``
.. _fileinput: https://docs.python.org/3/library/fileinput.html
