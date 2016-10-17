# Benefits: lets you specify the complete filename of the backup file, not just
# an extension; lets you control the encoding; doesn't redirect stdout; `read`
# method

# cf. <https://hg.python.org/cpython/file/2.7/Lib/fileinput.py#l310>

class InPlace(object):   ### Inherit one of the ABCs in `io`
    def __init__(self, filename, backup=None, backup_ext=None):
        ### Add options for encoding, newlines, binary vs. text mode,
        ### buffering?, encoding error handling, etc.

        ### Add `readhook` and `writehook` options for controlling how to open
        ### the filehandles for reading & writing?

        ### Create a separate class (`InPlaceBytes`?) for operating in binary
        ### mode?

        self.filename = filename
        if backup is not None:
            self.backup = backup
        elif backup_ext is not None:
            self.backup = filename + backup_ext
        else:
            self.backup = True
        self._editing = False
        self._infile = None
        self._outfile = None

    def __enter__(self):
        self._editing = True
        if self.backup is not None:
            ### Move file to backup location
        else:
            ### Move file to temporary location
        ### Open filehandles
        return self

    ### Alternative: Direct _outfile to a temporary file and only move things
    ### when done; cf. GNU sed
    ### <http://git.savannah.gnu.org/cgit/sed.git/tree/sed/sed.c#n84>

    def __exit__(self, exc_type, exc_value, traceback):
        ### Close filehandles
        if exc_type is not None:
            ### Delete new file and replace with backup file
        elif self.backup is None:
            ### Delete backup file
        self._editing = False
        return False

    def read(self, size=-1):
        return self._infile.read(size)

    def readline(self, size=-1):
        return self._infile.readline(size)

    def readlines(self, sizehint=-1):
        return self._infile.readlines(sizehint)

    def write(self, s):
        self._outfile.write(s)

    def writelines(self, seq):
        self._outfile.writelines(seq)

    def __iter__(self):
        return iter(self._infile)

    def close
    def flush
    def readinto  ### for binary streams, at least
