v0.2.0 (2017-02-23)
-------------------
- Renamed `InPlace` to `InPlaceText` and added a new `InPlace` class for
  reading & writing `str` objects (whatever those happen to be in the current
  Python)
- **Bugfix**: If the given file does not exist and `move_first` is `True`, an
  empty file will no longer be left behind in the nonexistent file's place.
- Specifying both `backup` and `backup_ext` will now produce a `ValueError`
- Specifying an empty `backup_ext` will now produce a `ValueError`

v0.1.1 (2017-01-27)
-------------------
Rename package & module from "`inplace`" to "`in_place`"  (I could have sworn I
had already checked PyPI for name conflicts....)

v0.1.0 (2017-01-27)
-------------------
Initial release
