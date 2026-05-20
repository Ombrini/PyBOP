from pybop.plot.plotly import PlotlyManager
from pybop.plot.util import _AxisData


def _check_empty(specs, row, col):
    if specs[row - 1][col - 1] is None or len(specs[row - 1][col - 1]) > 0:
        raise ValueError("Overlapping axes are not supported")


def create_figure(traces=None, **layout_options):
    go = PlotlyManager().go
    layout = go.Layout(**layout_options)
    fig = go.Figure(data=traces, layout=layout)
    return fig

def legend(fig, **kwargs):
    fig.update_layout(showlegend=True, **kwargs)

def update_layout(fig, axes=None, **layout_options):
    fig.update_layout(**layout_options)


def make_subplots(axes: list[_AxisData], subplot_options=None):
    subplot_options = subplot_options or {}

    num_rows = max(ax.row + ax.row_span - 1 for ax in axes)
    num_cols = max(ax.col + ax.col_span - 1 for ax in axes)
    specs = [[{}] * num_cols for _ in range(num_rows)]

    for ax in axes:
        _check_empty(specs, ax.row, ax.col)
        specs[ax.row - 1][ax.col - 1] = {"colspan": ax.col_span, "rowspan": ax.row_span}
        for row in range(ax.row, ax.row + ax.row_span - 1):
            for col in range(ax.col, ax.col + ax.col_span - 1):
                if row > ax.row or col > ax.col:
                    _check_empty(specs, row, col)
                    specs[row - 1, col - 1] = None

    make_subplots = PlotlyManager().make_subplots
    fig = make_subplots(rows=num_rows, cols=num_cols, specs=specs, **subplot_options)

    return fig

def show_figure(fig):
    if hasattr(fig, "__len__") and len(fig) > 0:
        for f in fig:
            f.show()
    else:
        fig.show()
