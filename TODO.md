- Add docstrings

- Write more tests:
    - Test the current directory changing between calls to `__init__`,
      `__enter__`, and `__exit__`
    - copying file mode, owner, & group
    - encodings
    - encoding error handler
    - newlines
    - bytes
    - `print`ing to an in-place file
    - every I/O method
    - handling of symbolic links
    - deleting the file before closing

- Add options for:
    - buffering?
    - `move_first=False` — when `True`, move the file and create a new one in
      its place on opening (à la `fileinput`) rather than creating a tempfile
      and only moving it on closing (as is done by GNU sed and Click's
      "atomic")
    - preserving the tempfile if an error was raised
    - Add `readhook` and `writehook` options for controlling how to open the
      filehandles for reading & writing?
        - Alternatively, if the user wants to override the opening methods, ey
          can just write a subclass
    - setting the directory in which to create the tempfile
    - forcing `backup` to be interpreted as relative to
      `os.path.dirname(filename)`?

- Support calling `rollback` and `close` in the middle of a `with` context?
- Get pytest to clean up its temporary directories
- When the filename is `-`, read stdin and write to stdout?
    - Only support this when an `allow_dash=True` argument is given?
- Skip Unix-specific `os` calls (e.g., `os.chown`) on platforms where they're
  not available
- Copy ACLs etc.
- Create the tempfile in the same directory as `filename` in order to ensure
  that the user can actually write to that directory
    - `sed` does this, apparently
- Feed `.coverage` files to Coveralls
- `sed` behavior to possibly copy:
    - If moving the input file to the backup path fails, delete the output
      tempfile and re-raise the error 
    - If moving the output tempfile to the input filepath fails, delete the
      output tempfile and re-raise the error

- Add the following methods:
    - `closed` (property)
    - `flush`
    - `readinto` (for binary files, at least)
