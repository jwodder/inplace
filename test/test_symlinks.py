from os                 import symlink
from os.path            import islink
from in_place           import InPlace
from test_in_place_util import TEXT, pylistdir

def test_symlink_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    realdir = tmpdir.mkdir('real')
    real = realdir.join('realfile.txt')
    real.write(TEXT)
    linkdir = tmpdir.mkdir('link')
    link = linkdir.join('linkfile.txt')
    symlink('../real/realfile.txt', str(link))
    with InPlace(str(link)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(realdir) == ['realfile.txt']
    assert pylistdir(linkdir) == ['linkfile.txt']
    assert islink(str(link))
    assert link.readlink() == '../real/realfile.txt'
    assert link.read() == TEXT.swapcase()
    assert real.read() == TEXT.swapcase()

def test_symlink_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    realdir = tmpdir.mkdir('real')
    real = realdir.join('realfile.txt')
    real.write(TEXT)
    linkdir = tmpdir.mkdir('link')
    link = linkdir.join('linkfile.txt')
    symlink('../real/realfile.txt', str(link))
    with InPlace(str(link), backup_ext='~') as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(realdir) == ['realfile.txt']
    assert pylistdir(linkdir) == ['linkfile.txt', 'linkfile.txt~']
    assert islink(str(link))
    assert link.readlink() == '../real/realfile.txt'
    assert link.new(ext='txt~').read() == TEXT
    assert link.read() == TEXT.swapcase()
    assert real.read() == TEXT.swapcase()

def test_symlink_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    realdir = tmpdir.mkdir('real')
    real = realdir.join('realfile.txt')
    real.write(TEXT)
    linkdir = tmpdir.mkdir('link')
    link = linkdir.join('linkfile.txt')
    symlink('../real/realfile.txt', str(link))
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(link), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'link', 'real']
    assert pylistdir(realdir) == ['realfile.txt']
    assert pylistdir(linkdir) == ['linkfile.txt']
    assert islink(str(link))
    assert link.readlink() == '../real/realfile.txt'
    assert bkp.read() == TEXT
    assert link.read() == TEXT.swapcase()
    assert real.read() == TEXT.swapcase()
