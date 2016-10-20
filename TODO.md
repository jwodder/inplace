- Write a README
- Fill in `description` and `keywords` in `setup.py`
- Integrate with Travis

- Write more tests:
    - Test the current directory changing between calls to `__init__`,
      `__enter__`, and `__exit__`
    - copying permissions and other file attributes
    - encodings
    - newlines
    - bytes

- Add options for:
    - encoding, newlines, binary vs. text mode, buffering?, encoding error
      handling, etc.
    - using a tempfile for the outfile instead of the infile and only moving
      files around when done; cf. GNU sed
      <http://git.savannah.gnu.org/cgit/sed.git/tree/sed/sed.c#n84>
    - preserving the tempfile if an error was raised
    - Add `readhook` and `writehook` options for controlling how to open the
      filehandles for reading & writing?
    - setting the directory in which to create the tempfile
    - forcing `backup` to be interpreted as relative to
      `os.path.dirname(filename)`?

- Copy file owner & group?
- Support calling `discard` and `close` in the middle of a `with` context?
- Create a separate class (`InPlaceBytes`?) for operating in binary mode?

- Add the following methods:
    - `flush`
    - `readinto` (for binary files, at least)
