- Add docstrings

- Write more tests:
    - Test the current directory changing between calls to `__init__`,
      `__enter__`, and `__exit__`
    - copying permissions and other file attributes
    - encodings
    - encoding error handler
    - newlines
    - bytes
    - `print`ing to an in-place file
    - Test every I/O method
    - rolling back on exceptions
    - handling of symbolic links
    - copying file owner & group

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

- Support calling `discard` and `close` in the middle of a `with` context?
- Get pytest to clean up its temporary directories
- The context manager is not reentrant; make sure it is not used as such
- When the filename is `-`, read stdin and write to stdout?
- Rename `discard` to `rollback`?
- Skip Unix-specific `os` calls (e.g., `os.chown`) on platforms where they're
  not available
- Copy ACLs etc.
- Create the tempfile in the same directory as `filename` in order to ensure
  that the user can actually write to that directory
- Feed `.coverage` files to Coveralls

- Add the following methods:
    - `closed` (property)
    - `flush`
    - `readinto` (for binary files, at least)
