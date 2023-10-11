- Somewhere document exactly how the module works with regards to creating
  temporary files and moving things around

- Add options for:
    - not resolving symbolic links
    - preserving the tempfile if an error was raised
    - `create=False`: If true and the input file doesn't exist, act as though
      it's simply empty

- Should calling `rollback` while closed be a no-op?
- Give `InPlace` a decent `__repr__`
