import ntab

#-------------------------------------------------------------------------------

def test_from_row_seqs():
    tab = ntab.from_row_seqs(
        ("foo", "bar", "baz"),
        [
            ( 3.14, 10, "Hello!"),
            ( 2.17, 20, "Good bye."),
            ( 0.00, 30, "What??"),
            (-1.00, 40, "Maybe..."),
        ]
    )
    assert list(tab.arrs.keys()) == ["foo", "bar", "baz"]
    assert len(tab.rows) == 4
    assert tab.a.foo[1] == 2.17
    assert tab.rows[3].baz == "Maybe..."


