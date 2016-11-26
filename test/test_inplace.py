import pytest
from   inplace import InPlace

TEXT = '''\
'Twas brillig, and the slithy toves
	Did gyre and gimble in the wabe;
All mimsy were the borogoves,
	And the mome raths outgrabe.

"Beware the Jabberwock, my son!
	The jaws that bite, the claws that catch!
Beware the Jubjub bird, and shun
	The frumious Bandersnatch!"

He took his vorpal sword in hand:
	Long time the manxome foe he sought--
So rested he by the Tumtum tree,
	And stood awhile in thought.

And as in uffish thought he stood,
	The Jabberwock, with eyes of flame,
Came whiffling through the tulgey wood,
	And burbled as it came!

One, two!  One, two!  And through and through
	The vorpal blade went snicker-snack!
He left it dead, and with its head
	He went galumphing back.

"And hast thou slain the Jabberwock?
	Come to my arms, my beamish boy!
O frabjous day!  Callooh!  Callay!"
	He chortled in his joy.

'Twas brillig, and the slithy toves
	Did gyre and gimble in the wabe;
All mimsy were the borogoves,
	And the mome raths outgrabe.
'''

def pylistdir(d): return sorted(p.basename for p in d.listdir())

def test_inplace_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_inplace_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_inplace_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_inplace_backup_chdir(tmpdir, monkeypatch):
    assert pylistdir(tmpdir) == []
    monkeypatch.chdir(tmpdir)
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup='backup.txt') as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert tmpdir.join('backup.txt').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_inplace_backup_ext_error(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(RuntimeError):
        with InPlace(str(p), backup_ext='~') as fp:
            for i, line in enumerate(fp):
                fp.write(line.swapcase())
                if i > 5:
                    raise RuntimeError("I changed my mind.")
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_inplace_nobackup_pass(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)):
        pass
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == ''

def test_inplace_delete_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for i, line in enumerate(fp):
            fp.write(line.swapcase())
            if i == 5:
                p.remove()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_inplace_delete_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(OSError):
        with InPlace(str(p), backup=str(bkp)) as fp:
            for i, line in enumerate(fp):
                fp.write(line.swapcase())
                if i == 5:
                    p.remove()
    assert pylistdir(tmpdir) == []

def test_inplace_early_close_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.close()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_inplace_early_close_and_write_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(ValueError):
        with InPlace(str(p)) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.close()
            fp.write('And another thing...\n')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_inplace_early_close_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.close()
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_inplace_early_close_and_write_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(ValueError):
        with InPlace(str(p), backup=str(bkp)) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.close()
            fp.write('And another thing...\n')
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_inplace_rollback_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_inplace_rollback_and_write_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(ValueError):
        with InPlace(str(p)) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.rollback()
            fp.write('And another thing...\n')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_inplace_rollback_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_inplace_rollback_and_write_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(ValueError):
        with InPlace(str(p), backup=str(bkp)) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.rollback()
            fp.write('And another thing...\n')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_inplace_backup_overwrite(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    bkp.write('This is not the file you are looking for.\n')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_inplace_rollback_backup_overwrite(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    bkp.write('This is not the file you are looking for.\n')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == 'This is not the file you are looking for.\n'
    assert p.read() == TEXT
