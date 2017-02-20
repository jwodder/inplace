- Create a Readthedocs site?
- Somewhere document exactly how the module works with regards to creating
  temporary files and moving things around

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
    - context manager re-entrancy
    - nonwritable directories

- Add options for:
    - preserving the tempfile if an error was raised
    - setting the directory in which to create the tempfile?
    - Don't error if moving the input file to the backup location fails?
    - not rolling back on error?
    - `create=False`: If true and the input file doesn't exist, act as though
      it's simply empty

- When the filename is `-`, read stdin and write to stdout?
    - Only support this when an `allow_dash=True` argument is given?
- Copy ACLs etc.
- Make `InPlaceABC` inherit one of the ABCs in `io`?
- How should exceptions raised by `_close` be handled?
- Should calling `rollback` while closed be a no-op?
- Use `shutil.move` instead of `os.rename` in order to handle cross-filesystem
  moves?  (But then strange things will happen when moving to a directory)
- Add a `commit` method that overwrites the input file with the output file's
  current contents but leaves the instance open afterwards?
- Give the classes decent `__repr__`s
