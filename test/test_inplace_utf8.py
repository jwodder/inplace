# -*- coding: utf-8 -*-
from   unicodedata import normalize
from   six         import text_type
from   inplace     import InPlace

TEXT = u'\xE5\xE9\xEE\xF8\xFC\n'  # u'àéîøü\n'

def pylistdir(d): return sorted(p.basename for p in d.listdir())

def test_inplace_utf8(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(TEXT, 'utf-8')
    with InPlace(str(p), encoding='utf-8') as fp:
        txt = fp.read()
        assert isinstance(txt, text_type)
        assert txt == TEXT
        fp.write(normalize('NFD', txt))
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_text('utf-8') == u'a\u030Ae\u0301i\u0302\xF8u\u0308\n'
