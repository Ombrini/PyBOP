import math
from copy import deepcopy

import numpy as np

from pybop.plot.util import (
    _AxisData,
    import_backend,
    wrap_text,
    parse_data
)

class Subplots():

    def __init__(
        self,
        x=None,
        y=None,
        num_rows=None,
        num_cols=None,
        num_plots=None,
        backend=None,
    ):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_plots = num_plots

        if x is not None and y is not None:
            self.x, self.y = parse_data(x, y)
            if self.num_plots is None:
                self.num_plots = len(self.y)
        else: 
            self.x = None
            self.y = None


        self.backend = import_backend(backend)
    
        if self.num_rows == None and self.num_cols == None:
            if self.num_plots is not None:
                # Work out the number of subplots
                self.num_cols = int(math.ceil(math.sqrt(self.num_plots)))
                self.num_rows = int(math.ceil(self.num_plots/ self.num_cols))
        elif self.num_rows is None:
            if self.num_plots is None:
                self.num_rows = 1
                self.num_plots = self.num_cols
            else:
                self.num_rows = int(math.ceil(self.num_plots/ self.num_cols))
        elif self.num_cols is None:
            if self.num_plots is None:
                self.num_cols = 1
                self.num_plots = self.num_rows
            else:
                self.num_cols = int(math.ceil(self.num_traces / self.num_rows))

        if self.num_plots is not None:
            self._axes_data = [
                _AxisData(row + 1, col + 1)
                for row in range(self.num_rows)
                for col in range(self.num_cols)
            ]
        else: 
            self._axes_data = []

        self.fig = None
        self.axes = None

    def add_axis_data(self, row, col, row_span=1, col_span=1):
        self._axes_data.append(_AxisData(row, col, row_span, col_span))

    def create_figure(self, title=None, axis_titles_x: list[str] | str = None, axis_titles_y: list[str] | str = None, style=None):
        self.fig, self.axes, self.num_rows, self.num_cols = self.backend.make_subplots(self._axes_data, title=title, axis_titles_x=axis_titles_x, axis_titles_y=axis_titles_y, style=style)

    def get_axis(self, row, col):
        if self.axes is None:
            raise ValueError("Figure contains no axes or has not been created.")
        
        if (row, col) in self.axes.keys():
            return self.axes[(row, col)]
        else:
            raise KeyError(f"No axes for row={row} and col={col} found.")
        
    def plot_lines(self, x=None, y=None, labels=None):
        if self.fig is None:
            self.create_figure()
        if x is None:
            if self.x is None:
                raise ValueError("No data for plotting supplied.")
            else:
                x = self.x
        if y is None:
            if self.y is None:
                raise ValueError("No data for plotting supplied.")
            else:
                y = self.y
        x, y = parse_data(x, y)
        xi = x[0]
        for i in range(0, len(y)):
            row = (i // self.num_cols) + 1
            col = (i % self.num_cols) + 1
            if row > self.num_rows:
                row = (row % self.num_rows) + 1
            if len(x) > 1:
                xi = x[i]
            label = None
            if labels is not None:
                label = labels[i]

            self.backend.plot_trace(self.backend.line_plot(xi, y[i], label), self.fig, ax=self.get_axis(row, col))


def trajectories(x, y, xaxis_title: str = None, yaxis_title: str = None, labels=None, title:str = None, show=True, backend=None, label_width=20):
    """
    Quickly plot one or more trajectories using Plotly.

    Parameters
    ----------
    x : list or np.ndarray
        X-axis data points.
    y : list or np.ndarray
        Y-axis data points for each trajectory.
    trace_names : list or str, optional
        Name(s) for the trace(s) (default: None).
    **layout_kwargs : optional
            Valid Plotly layout keys and their values,
            e.g. `xaxis_title="Time / s"` or
            `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """

    # Check and wrap trace names
    if labels is not None:
        if isinstance(labels, str):
            labels = [labels]
        for i, name in enumerate(labels):
            labels[i] = wrap_text(
                name, width=label_width, backend=backend
            )

    backend = import_backend(backend)
    fig = backend.create_figure(
        title = title,
        xaxis_title = xaxis_title,
        yaxis_title = yaxis_title,
        style = {
            "height" : 600,
            "width" : 600,
            "bg_color" : "white"
        }
    )

    x, y = parse_data(x, y)
    xi = x[0]
    for i in range(0, len(y)):
        if len(x) > 1:
            xi = x[i]
        label = None
        if labels is not None:
            label = labels[i]

        backend.plot_trace(backend.line_plot(xi, y[i], label), fig)
    
    backend.legend(fig)

    if show:
        backend.show_figure(fig)
    return fig