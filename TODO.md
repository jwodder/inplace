- Add docstrings
- cf. <https://hg.python.org/cpython/file/2.7/Lib/fileinput.py#l310>

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
    - using a tempfile for the outfile instead of the infile and only moving
      files around when done
        - cf. GNU sed:
          <http://git.savannah.gnu.org/cgit/sed.git/tree/sed/sed.c#n84>
        - cf. the "atomic" option in Click
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
- Don't copy the input file, just move it?  (This is vulnerable to race
  conditions.)
- Skip Unix-specific `os` calls (e.g., `os.chown`) on platforms where they're
  not available
- Copy ACLs etc.
- Create the tempfile in the same directory as `filename` in order to ensure
  that the user can actually write to that directory

- Add the following methods:
    - `closed` (property)
    - `flush`
    - `readinto` (for binary files, at least)
