- Somewhere document exactly how the module works with regards to creating
  temporary files and moving things around

- Write more tests:
    - copying file mode, timestamps, owner, & group
    - timestamp (and other file attributes?) preservation on rollback
    - newlines
    - every I/O method
        - flush
        - readall
    - Assert that the tempfile is created in the right directory
    - `delay_open=True`
    - nontrivial (i.e., containing `/` and/or `..`) relative filepaths
    - `backup_ext` containing a directory separator?
    - `backup_ext` when the filepath contains a directory separator
    - relative vs. absolute paths?
    - context manager non-reusability
    - nonwritable directories
    - symlinks pointing to nonexistent files

- Add options for:
    - preserving the tempfile if an error was raised
    - Don't error if moving the input file to the backup location fails?
    - `rollback_on_error=True`
    - `create=False`: If true and the input file doesn't exist, act as though
      it's simply empty
    - not resolving symbolic links?

- When the filename is `-`, read stdin and write to stdout?
    - Only support this when an `allow_dash=True` argument is given?
- Copy ACLs etc.
- Make `InPlace` inherit one of the ABCs in `io`?
- How should exceptions raised by `_close` be handled?
- Should calling `rollback` while closed be a no-op?
- Use `shutil.move` instead of `os.rename` in order to handle cross-filesystem
  moves?  (But then strange things will happen when moving to a directory)
- Add a `commit` method that overwrites the input file with the output file's
  current contents but leaves the instance open afterwards?
- Give `InPlace` a decent `__repr__`s
- Make the context manager reusable
- Add a `seekable()` method that returns `False`?
