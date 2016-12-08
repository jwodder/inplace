- Add docstrings
- Create a Readthedocs site?

- Write more tests:
    - copying file mode, timestamps, owner, & group
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
    - `move_first=True`

- Add options for:
    - buffering?
    - preserving the tempfile if an error was raised
    - Add `readhook` and `writehook` options for controlling how to open the
      filehandles for reading & writing?
        - Alternatively, if the user wants to override the opening methods, ey
          can just write a subclass
    - setting the directory in which to create the tempfile?
    - Don't error if moving the input file to the backup location fails?

- When the filename is `-`, read stdin and write to stdout?
    - Only support this when an `allow_dash=True` argument is given?
- Copy ACLs etc.
- Make `InPlaceABC` inherit one of the ABCs in `io`?
- How should exceptions raised by `_close` be handled?
- `move_first=True`: The input file should be moved to a temporary path and
  only moved to the backup path on successful completion; this way, if a
  rollback occurs, whatever was already at the backup path will be untouched.

- Get pytest to clean up its temporary directories
- Feed `.coverage` files to Coveralls
- Test against & add support for pypy?
