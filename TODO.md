- Somewhere document exactly how the module works with regards to creating
  temporary files and moving things around

- Write more tests:
    - copying file mode, timestamps, owner, & group
    - timestamp (and other file attributes?) preservation on rollback
    - newlines
    - every I/O method
    - Assert that the tempfile is created in the right directory
    - nontrivial (i.e., containing `/` and/or `..`) relative filepaths
    - `backup_ext` containing a directory separator?
    - `backup_ext` when the filepath contains a directory separator
    - relative vs. absolute paths?
    - context manager non-reusability
    - nonwritable directories
    - symlinks pointing to nonexistent files

- Add options for:
    - not resolving symbolic links
    - preserving the tempfile if an error was raised
    - `create=False`: If true and the input file doesn't exist, act as though
      it's simply empty

- How should exceptions raised by `_close` be handled?
- Should calling `rollback` while closed be a no-op?
- Give `InPlace` a decent `__repr__`s
- Make the context manager reusable
