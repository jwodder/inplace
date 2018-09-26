import pytest
from   in_place           import InPlace
from   test_in_place_util import TEXT, pylistdir

@pytest.mark.parametrize('move_first', [True, False])
@pytest.mark.parametrize('backup', [None, 'backup.txt'])
def test_bad_mode(tmpdir, move_first, backup):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with pytest.raises(ValueError, match='invalid mode'):
        InPlace(str(p), mode='q', move_first=move_first, backup=backup)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

@pytest.mark.parametrize('move_first', [True, False])
@pytest.mark.parametrize('backup', [None, 'backup.txt'])
def test_bad_mode_delay_open_with(tmpdir, move_first, backup):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    fp = InPlace(
        str(p),
        mode       = 'q',
        delay_open = True,
        move_first = move_first,
        backup     = backup,
    )
    with pytest.raises(ValueError, match='invalid mode'):
        with fp:
            assert False
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT

@pytest.mark.parametrize('move_first', [True, False])
@pytest.mark.parametrize('backup', [None, 'backup.txt'])
def test_bad_mode_delay_open_open(tmpdir, move_first, backup):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    fp = InPlace(
        str(p),
        mode       = 'q',
        delay_open = True,
        move_first = move_first,
        backup     = backup,
    )
    with pytest.raises(ValueError, match='invalid mode'):
        fp.open()
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT
