from   __future__        import print_function
from   inplace           import InPlace
from   test_inplace_util import TEXT, pylistdir

def test_print_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            print(line.swapcase(), end=u'', file=fp)
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()
