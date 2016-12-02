- Add docstrings
- Create a Readthedocs site?

- Write more tests:
    - copying file mode, owner, & group
    - encodings
    - encoding error handler
    - newlines
    - bytes
    - `print`ing bytes?
    - `print`ing Unicode?
    - every I/O method
    - handling of symbolic links
    - Assert that the tempfile is created in the right directory
    - Assert that all of the relevant attributes on an `InPlace` object are
      `None` after closing (and non-`None` before closing)
    - neglecting a needed directory path for `backup`
    - `delay_open=True`
    - invalid backup path (e.g., a pre-existing directory)

- Add options for:
    - buffering?
    - `move_first=False` — when `True`, move the file and create a new one in
      its place on opening (à la `fileinput`) rather than creating a tempfile
      and only moving it on closing (as is done by GNU sed and Click's
      "atomic")
        - Specifically, the input file should be moved to a temporary path and
          only moved to the backup path on successful completion; this way, if
          a rollback occurs, whatever was already at the backup path will be
          untouched.
    - preserving the tempfile if an error was raised
    - Add `readhook` and `writehook` options for controlling how to open the
      filehandles for reading & writing?
        - Alternatively, if the user wants to override the opening methods, ey
          can just write a subclass
    - setting the directory in which to create the tempfile?
    - Don't error if moving the input file to the backup location fails?

- When the filename is `-`, read stdin and write to stdout?
    - Only support this when an `allow_dash=True` argument is given?
- Skip Unix-specific `os` calls (e.g., `os.chown`) on platforms where they're
  not available
- Copy ACLs etc.
- Make `InPlaceABC` inherit one of the ABCs in `io`?

- Get pytest to clean up its temporary directories
- Feed `.coverage` files to Coveralls
- Test against & add support for pypy?
