import pytest
from unittest.mock import Mock, patch, sentinel

from grid_strategy.strategies import SquareStrategy


class SpecValue:
    def __init__(self, rows, cols, parent=None):
        self.rows = rows
        self.cols = cols
        self.parent = parent

    def __repr__(self):  # pragma: nocover
        return f"{self.__class__.__name__}({self.rows}, {self.cols})"

    def __eq__(self, other):
        return self.rows == other.rows and self.cols == other.cols


@pytest.fixture
def gridspec_mock():
    with patch("grid_strategy._abc.gridspec.GridSpec", new_callable=Mock) as g:
        g.return_value.__getitem__ = lambda self, key_tup: SpecValue(*key_tup, self)
        yield g


@pytest.fixture
def plt_figure_mock():
    with patch("grid_strategy._abc.plt.figure", new_callable=Mock) as f:
        f.return_value = sentinel.new_figure
        yield f


@pytest.mark.parametrize(
    "align, n, exp_specs",
    [
        ("center", 1, [(0, slice(0, 1))]),
        ("center", 2, [(0, slice(0, 1)), (0, slice(1, 2))]),
        ("center", 3, [(0, slice(0, 2)), (0, slice(2, 4)), (1, slice(1, 3))]),
        ("left", 3, [(0, slice(0, 2)), (0, slice(2, 4)), (1, slice(0, 2))]),
        ("right", 3, [(0, slice(0, 2)), (0, slice(2, 4)), (1, slice(2, 4))]),
        ("justified", 3, [(0, slice(0, 1)), (0, slice(1, 2)), (1, slice(0, 2))]),
        (
            "center",
            8,
            [
                (0, slice(0, 2)),
                (0, slice(2, 4)),
                (0, slice(4, 6)),
                (1, slice(1, 3)),
                (1, slice(3, 5)),
                (2, slice(0, 2)),
                (2, slice(2, 4)),
                (2, slice(4, 6)),
            ],
        ),
        ("left", 2, [(0, slice(0, 1)), (0, slice(1, 2))]),
    ],
)
@pytest.mark.parametrize("figure_passed", [True, False])
def test_square_spec(
    gridspec_mock, plt_figure_mock, align, n, exp_specs, figure_passed
):
    if figure_passed:
        user_figure = sentinel.user_figure
    else:
        user_figure = None

    ss = SquareStrategy(align)
    act = ss.get_grid(n, figure=user_figure)

    exp = [SpecValue(*spec) for spec in exp_specs]
    assert act == exp

    args, kwargs = gridspec_mock.call_args
    if figure_passed:
        plt_figure_mock.assert_not_called()
        assert kwargs["figure"] is sentinel.user_figure
    else:
        plt_figure_mock.assert_called_once_with(constrained_layout=True)
        assert kwargs["figure"] is sentinel.new_figure
