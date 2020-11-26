from in_place           import InPlace
from test_in_place_util import TEXT, UNICODE, pylistdir

def test_print_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            print(line.swapcase(), end='', file=fp)
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_readinto_bytearray_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p), 'b') as fp:
        ba = bytearray(5)
        assert fp.readinto(ba) == 5
        assert ba == bytearray(b'\xC3\xA5\xC3\xA9\xC3')
        fp.write(ba)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_binary() == b'\xC3\xA5\xC3\xA9\xC3'

def test_readlines_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        assert fp.readlines() == TEXT.splitlines(True)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == ''

def test_writelines_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write('')
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        fp.writelines(TEXT.splitlines(True))
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == ''
    assert p.read() == TEXT

def test_readline_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for line in iter(fp.readline, ''):
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()
