v1.0.0 (in development)
-----------------------
- Support Python 3.10, 3.11, and 3.12
- Drop support for Python 3.6 and 3.7
- **Breaking**: The `move_first` argument has been removed.  Only the
  `move_first=False` semantics are retained.
- Removed the `readall()` method.  I don't think it ever worked.
- **Breaking**: The `delay_open` argument and `open()` method have been
  removed.  Filehandles will now always be created at the moment an in-place
  instance is constructed, just like when calling the standard library's
  `open()`.
- **Breaking**: When the input path points to a symlink and `backup_ext` is
  given, the backup extension will now be appended to the resolved path rather
  than to the pre-resolved path.
- Added type annotations
- `InPlaceText` and `InPlaceBytes` (deprecated in v0.4.0) have been removed
- Added `read1()` and `readinto1()` methods for binary mode
- The `InPlace` constructor now immediately raises a `ValueError` if `backup`
  is the empty string

v0.5.0 (2021-02-20)
-------------------
- Support Python 3.8 and 3.9
- Drop support for Python 2.7, 3.4, and 3.5
- Support `move_first` on Windows
- Get tests to pass on Windows
- Use [`jaraco.windows`](https://github.com/jaraco/jaraco.windows) to handle
  symlinks on Windows on versions of Python prior to 3.8

v0.4.0 (2018-10-05)
-------------------
- **Breaking**: Combined all classes' functionality into a single `InPlace`
  class that uses a `mode` argument to determine whether to operate in text or
  binary mode.
- `InPlaceBytes` and `InPlaceText` are now deprecated and will be removed in a
  future version; please use `InPlace` with `mode='b'` or `mode='t'` instead.
- Support fsencoded-bytes as file paths under Python 3

v0.3.0 (2018-06-28)
-------------------
- Handling of symbolic links is changed: Now, if `in_place` is asked to operate
  on a symlink `link.txt` that points to `realfile.txt`, it will act as though
  it was asked to operate on `realfile.txt` instead, and the path `link.txt`
  will only be used when combining with `backup_ext` to construct a backup file
  path
- Drop support for Python 2.6 and 3.3

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
