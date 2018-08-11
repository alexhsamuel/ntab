from   pathlib import Path
import pickle
import pytest

from   ntab import Table

#-------------------------------------------------------------------------------

@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle0(tmpdir, protocol):
    path = Path(tmpdir) / "test_pickle0.pickle"

    tab = Table(dict(x=[1, 2, 3], y=[2, 3, 4], z=[3, 4, 5]))

    with path.open("wb") as file:
        pickle.dump(tab, file, protocol=protocol)
    with path.open("rb") as file:
        tab = pickle.load(file)

    assert tab.num_cols == 3
    assert tab.num_rows == 3
    assert sorted(tab.names) == ["x", "y", "z"]


