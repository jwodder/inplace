- Write a README
- Integrate with Travis
- Fill in `description` and `keywords` in `setup.py`
- Test the current directory changing between calls to `__init__`, `__enter__`,
  and `__exit__`
- Add an option for instead creating the outfile as a temporary file and only
  moving files around when done; cf. GNU sed
  <http://git.savannah.gnu.org/cgit/sed.git/tree/sed/sed.c#n84>
- Copy file mode, owner, etc.
- Add an option for preserving the tempfile if an error was raised
- Add options for encoding, newlines, binary vs. text mode, buffering?,
  encoding error handling, etc.
- Add `readhook` and `writehook` options for controlling how to open the
  filehandles for reading & writing?
- Create a separate class (`InPlaceBytes`?) for operating in binary mode?
- Add an option for setting the directory in which to create the tempfile
