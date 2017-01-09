- Add docstrings
    - Document that you should always close (or rollback) `InPlace` objects
      explicity, because we can't guarantee tmpfile cleanup on garbage
      collection
- Create a Readthedocs site?

- Write more tests:
    - copying file mode, timestamps, owner, & group
    - newlines
    - every I/O method
        - readline
        - readlines
        - writelines
        - `__iter__`
        - flush
        - readall
    - handling of symbolic links
    - Assert that the tempfile is created in the right directory
    - Assert that all of the relevant attributes on an `InPlace` object are
      `None` after closing (and non-`None` before closing)
    - `delay_open=True`
    - nontrivial (i.e., containing `/` and/or `..`) relative filepaths
    - `backup_ext` containing a directory separator?
    - `backup_ext` when the filepath contains a directory separator
    - relative vs. absolute paths?

- Add options for:
    - buffering?
    - preserving the tempfile if an error was raised
    - setting the directory in which to create the tempfile?
    - Don't error if moving the input file to the backup location fails?

- When the filename is `-`, read stdin and write to stdout?
    - Only support this when an `allow_dash=True` argument is given?
- Copy ACLs etc.
- Make `InPlaceABC` inherit one of the ABCs in `io`?
- How should exceptions raised by `_close` be handled?
- Should calling `rollback` while closed be a no-op?

- Get pytest to clean up its temporary directories
- Feed `.coverage` files to Coveralls
- Test against and indicate support for pypy & pypy3
- Test against and indicate support for Python 3.6
