from   tabela.lib import memo

#-------------------------------------------------------------------------------

def test_lazy_property():

    nfoo = 0
    nbar = 0

    class C:

        def __init__(self, x):
            self.__x = x

        @memo.lazy_property
        def foo(self):
            nonlocal nfoo
            nfoo += 1
            return self.__x

        @memo.lazy_property
        def bar(self):
            nonlocal nbar
            nbar += 1
            return 2 * self.__x + 1


    c0 = C(42)
    c1 = C(17)
    assert c0.foo == 42
    assert c0.foo == 42
    assert c0.bar == 85
    assert c0.bar == 85
    assert c1.foo == 17
    assert c1.bar == 35
    assert c1.foo == 17
    assert c0.bar == 85
    assert nfoo == 2
    assert nbar == 2


def test_lazy_property_private():

    class C:

        def __init__(self, x):
            self.__x = x

        @memo.lazy_property
        def __foo(self):
            x = self.__x
            self.__x = None
            return x

        @property
        def bar(self):
            return 2 * self.__foo + 1


    c = C(42)
    assert c._C__x == 42
    assert c.bar == 85
    assert c.bar == 85
    assert c.bar == 85
    assert c._C__foo == 42
    assert c._C__x is None


