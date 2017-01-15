- Add docstrings
    - Document that you should always close (or rollback) `InPlace` objects
      explicity, because we can't guarantee tmpfile cleanup on garbage
      collection
    - Emphasize that `InPlace` deals with `unicode` objects in Python 2
- Create a Readthedocs site?

- Write more tests:
    - copying file mode, timestamps, owner, & group
    - newlines
    - every I/O method
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
- Use `shutil.move` instead of `os.rename` in order to handle cross-filesystem
  moves?  (But then strange things will happen when moving to a directory)
- Raise an error if both `backup` and `backup_ext` are defined?
- Raise an error if `backup_ext` is empty?
- Use a standard exception instead of `DoubleOpenError`?
- Add an `InPlaceStr` class that just calls `open` without specifying encoding
  or bytesness?
    - Make this the default `InPlace` and rename the current `InPlace` to
      `InPlaceText`?

- Get pytest to clean up its temporary directories
- Feed `.coverage` files to Coveralls
- Test against and indicate support for pypy & pypy3
- Test against and indicate support for Python 3.6
