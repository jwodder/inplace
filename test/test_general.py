import os
import pytest
from   in_place           import InPlace
from   test_in_place_util import TEXT, pylistdir

def test_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        assert not fp.closed
        for line in fp:
            assert isinstance(line, str)
            fp.rewrite(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        assert not fp.closed
        for line in fp:
            fp.rewrite(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_backup_ext_and_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(ValueError):
        with InPlace(str(p), backup=str(bkp), backup_ext='~'):
            assert False
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_empty_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(ValueError):
        with InPlace(str(p), backup_ext=''):
            assert False
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_error_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(RuntimeError):
        with InPlace(str(p), backup_ext='~') as fp:
            for i, line in enumerate(fp):
                fp.rewrite(line.swapcase())
                if i > 5:
                    raise RuntimeError("I changed my mind.")
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_pass_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)):
        pass
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == ''

def test_delete_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for i, line in enumerate(fp):
            fp.rewrite(line.swapcase())
            if i == 5:
                p.remove()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_delete_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(OSError):
        with InPlace(str(p), backup=str(bkp)) as fp:
            for i, line in enumerate(fp):
                fp.rewrite(line.swapcase())
                if i == 5:
                    p.remove()
    assert pylistdir(tmpdir) == []

def test_early_close_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
        fp.close()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_early_close_and_write_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(ValueError):
        with InPlace(str(p)) as fp:
            for line in fp:
                fp.rewrite(line.swapcase())
            fp.close()
            fp.rewrite('And another thing...\n')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_early_close_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
        fp.close()
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_early_close_and_write_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(ValueError):
        with InPlace(str(p), backup=str(bkp)) as fp:
            for line in fp:
                fp.rewrite(line.swapcase())
            fp.close()
            fp.rewrite('And another thing...\n')
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_rollback_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
        fp.rollback()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_rollback_and_write_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(ValueError):
        with InPlace(str(p)) as fp:
            for line in fp:
                fp.rewrite(line.swapcase())
            fp.rollback()
            fp.rewrite('And another thing...\n')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_rollback_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
        fp.rollback()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_rollback_and_write_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with pytest.raises(ValueError):
        with InPlace(str(p), backup=str(bkp)) as fp:
            for line in fp:
                fp.rewrite(line.swapcase())
            fp.rollback()
            fp.rewrite('And another thing...\n')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_overwrite_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    bkp.write('This is not the file you are looking for.\n')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_rollback_overwrite_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    bkp.write('This is not the file you are looking for.\n')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
        fp.rollback()
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == 'This is not the file you are looking for.\n'
    assert p.read() == TEXT

def test_prechdir_backup(tmpdir, monkeypatch):
    assert pylistdir(tmpdir) == []
    monkeypatch.chdir(tmpdir)
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup='backup.txt') as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert tmpdir.join('backup.txt').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_midchdir_backup(tmpdir, monkeypatch):
    """
    Assert that changing directory between creating an InPlace object and
    opening it works
    """
    filedir = tmpdir.mkdir('filedir')
    wrongdir = tmpdir.mkdir('wrongdir')
    p = filedir.join("file.txt")
    p.write(TEXT)
    monkeypatch.chdir(filedir)
    fp = InPlace('file.txt', backup='backup.txt', delay_open=True)
    monkeypatch.chdir(wrongdir)
    assert fp.closed
    with fp:
        assert not fp.closed
        for line in fp:
            fp.rewrite(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert os.getcwd() == str(wrongdir)
    assert pylistdir(wrongdir) == []
    assert pylistdir(filedir) == ['backup.txt', 'file.txt']
    assert filedir.join('backup.txt').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_postchdir_backup(tmpdir, monkeypatch):
    """ Assert that changing directory after opening an InPlace object works """
    filedir = tmpdir.mkdir('filedir')
    wrongdir = tmpdir.mkdir('wrongdir')
    p = filedir.join("file.txt")
    p.write(TEXT)
    monkeypatch.chdir(filedir)
    with InPlace('file.txt', backup='backup.txt') as fp:
        monkeypatch.chdir(wrongdir)
        for line in fp:
            fp.rewrite(line.swapcase())
    assert os.getcwd() == str(wrongdir)
    assert pylistdir(wrongdir) == []
    assert pylistdir(filedir) == ['backup.txt', 'file.txt']
    assert filedir.join('backup.txt').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_different_dir_backup(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    filedir = tmpdir.mkdir('filedir')
    bkpdir = tmpdir.mkdir('bkpdir')
    p = filedir.join("file.txt")
    p.write(TEXT)
    with InPlace(
        os.path.join('filedir', 'file.txt'),
        backup=os.path.join('bkpdir', 'backup.txt')
    ) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    assert pylistdir(filedir) == ['file.txt']
    assert pylistdir(bkpdir) == ['backup.txt']
    assert bkpdir.join('backup.txt').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_different_dir_file_backup(tmpdir, monkeypatch):
    """
    Assert that if the input filepath contains a directory component and the
    backup path does not, the backup file will be created in the current
    directory
    """
    monkeypatch.chdir(tmpdir)
    filedir = tmpdir.mkdir('filedir')
    p = filedir.join("file.txt")
    p.write(TEXT)
    with InPlace(
        os.path.join('filedir', 'file.txt'),
        backup='backup.txt',
    ) as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['backup.txt', 'filedir']
    assert pylistdir(filedir) == ['file.txt']
    assert tmpdir.join('backup.txt').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_backup_dirpath(tmpdir):
    """
    Assert that using a path to a directory as the backup path raises an error
    when closing
    """
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    not_a_file = tmpdir.join('not-a-file')
    not_a_file.mkdir()
    assert pylistdir(not_a_file) == []
    fp = InPlace(str(p), backup=str(not_a_file))
    fp.rewrite('This will be discarded.\n')
    with pytest.raises(EnvironmentError):
        fp.close()
    assert pylistdir(tmpdir) == ['file.txt', 'not-a-file']
    assert p.read() == TEXT
    assert pylistdir(not_a_file) == []

def test_backup_nosuchdir(tmpdir):
    """
    Assert that using a path to a file in a nonexistent directory as the backup
    path raises an error when closing
    """
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    fp = InPlace(str(p), backup=str(tmpdir.join('nonexistent', 'backup.txt')))
    fp.rewrite('This will be discarded.\n')
    with pytest.raises(EnvironmentError):
        fp.close()
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

def test_double_open_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p)) as fp:
        with pytest.raises(ValueError):
            fp.open()
        assert not fp.closed
        for line in fp:
            fp.rewrite(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

def test_nonexistent(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    fp = InPlace(str(p), delay_open=True)
    with pytest.raises(EnvironmentError):
        fp.open()
    assert pylistdir(tmpdir) == []

def test_with_nonexistent(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    with pytest.raises(EnvironmentError):
        with InPlace(str(p)):
            assert False
    assert pylistdir(tmpdir) == []

def test_nonexistent_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    fp = InPlace(str(p), backup_ext='~', delay_open=True)
    with pytest.raises(EnvironmentError):
        fp.open()
    assert pylistdir(tmpdir) == []

def test_with_nonexistent_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    with pytest.raises(EnvironmentError):
        with InPlace(str(p), backup_ext='~'):
            assert False
    assert pylistdir(tmpdir) == []

def test_reentrant_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        with fp:
            for line in fp:
                fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_use_and_reenter_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        fp.write(fp.readline().swapcase())
        with fp:
            for line in fp:
                fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_var_changes(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        assert not fp.closed
        assert fp.input is not None
        assert fp.output is not None
        assert fp._tmppath is not None
        assert fp._state == fp.OPEN
    assert fp.closed
    assert fp.input is None
    assert fp.output is None
    assert fp._tmppath is None
    assert fp._state == fp.CLOSED

def test_useless_after_close(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        assert not fp.closed
    assert fp.closed
    with pytest.raises(ValueError):
        fp.flush()
    with pytest.raises(ValueError):
        iter(fp)
    with pytest.raises(ValueError):
        fp.read()
    with pytest.raises(ValueError):
        fp.readline()
    with pytest.raises(ValueError):
        fp.readlines()
    with pytest.raises(ValueError):
        fp.rewrite('')
    with pytest.raises(ValueError):
        fp.rewritelines([''])

def test_rollback_too_late(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(str(p), backup_ext='~') as fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    with pytest.raises(ValueError):
        fp.rollback()
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

def test_rollback_too_early(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    fp = InPlace(str(p), backup_ext='~', delay_open=True)
    with pytest.raises(ValueError):
        fp.rollback()
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT
    with fp:
        for line in fp:
            fp.rewrite(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()
