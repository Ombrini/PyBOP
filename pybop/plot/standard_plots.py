import math
import textwrap

import numpy as np

from pybop.plot.util import call_plotting_function


class StandardPlot:
    def __init__(
        self,
        x=None,
        y=None,
        trace_options=None,
        trace_names=None,
        trace_name_width=20,
        backend=None,
        **kwargs,
    ):

        self.plotter = call_plotting_function(
            "Plotter", backend, trace_options=trace_options, **kwargs
        )

        self.trace_name_width = trace_name_width

        # Add traces
        if x is not None and y is not None:
            self.add_traces(x, y, trace_names)

    def __call__(self, show=True):
        return self.plotter(show=show)

    @property
    def traces(self):
        return self.plotter.traces

    @traces.setter
    def traces(self, value):
        self.plotter.traces = value

    def add_traces(self, x, y, trace_names):
        # Check and wrap trace names
        if trace_names is not None:
            if isinstance(trace_names, str):
                trace_names = [trace_names]
            for i, name in enumerate(trace_names):
                trace_names[i] = self.wrap_text(
                    name, width=self.trace_name_width, backend=self.plotter.backend
                )

        # Parse the data
        x, y = self.parse_data(x, y)

        # Add traces
        self.plotter.add_traces(x, y, trace_names)

    def parse_data(self, x, y):
        """
        Check the type and dimensions of the data and convert if necessary to a list
        of 'things plotly can take', e.g. numpy arrays or lists of numbers.

        Parameters
        ----------
        x : list or np.ndarray, optional
            X-axis data points.
        y : list or np.ndarray, optional
            Primary Y-axis data points for simulated model output.
        """
        if isinstance(x, list):
            # If it's a list of numpy arrays, it's fine
            # If it's a list of lists, it's fine
            # If it's neither, it's a list of numbers that we need to wrap
            if not isinstance(x[0], np.ndarray) and not isinstance(x[0], list):
                x = [x]
        elif isinstance(x, np.ndarray):
            x = np.squeeze(x)
            if x.ndim == 1:
                x = [x]
            else:
                x = x.tolist()
        if isinstance(y, list):
            if not isinstance(y[0], np.ndarray) and not isinstance(y[0], list):
                y = [y]
        if isinstance(y, np.ndarray):
            y = np.squeeze(y)
            if y.ndim == 1:
                y = [y]
            else:
                y = y.tolist()
        if len(x) > 1 and len(x) != len(y):
            raise ValueError(
                "Input x should have either one data series or the same number as y."
            )
        return x, y

    def create_trace(self, x, y, **trace_options):
        return self.plotter.create_trace(x, y, **trace_options)
    
    def create_fill_trace(self, x, y_upper, y_lower, **options):
        return self.plotter.create_fill_trace(x, y_upper, y_lower, **options)

    @staticmethod
    def wrap_text(text, width, backend="matplotlib"):
        """
        Wrap text to a specified width with HTML line breaks.

        Parameters
        ----------
        text : str
            The text to wrap.
        width : int
            The width to wrap the text to.

        Returns
        -------
        str
            The wrapped text.
        """
        wrapped_text = textwrap.fill(text, width=width, break_long_words=False)
        if backend == "plotly":
            return wrapped_text.replace("\n", "<br>")
        else:
            return wrapped_text

    @staticmethod
    def remove_brackets(s):
        """
        Remove square brackets from a string and replace with forward slashes
        as per section 7.1 of the SI Handbook
        """
        # If s is an iterable (but not a string), apply the function recursively to each element
        if hasattr(s, "__iter__") and not isinstance(s, str):
            return type(s)(StandardPlot.remove_brackets(i) for i in s)
        elif isinstance(s, str):
            start = s.find("[")
            end = s.find("]")
            if start != -1 and end != -1:
                char_in_brackets = s[start + 1 : end]
                return s[:start] + " / " + char_in_brackets + s[end + 1 :]
        return s


class StandardSubplot(StandardPlot):
    """
    A class for creating and displaying a set of interactive Plotly figures in a grid layout.

    Parameters
    ----------
    x : list or np.ndarray
        X-axis data points.
    y : list or np.ndarray
        Primary Y-axis data points for simulated model output.
    num_rows : int, optional
        Number of rows of subplots, can be set automatically (default: None).
    num_cols : int, optional
        Number of columns of subplots, can be set automatically (default: None).
    layout : Plotly layout, optional
        A layout for the figure, overrides the layout options (default: None).
    layout_options : dict, optional
        Settings to modify the default layout (default: DEFAULT_LAYOUT_OPTIONS).
    trace_options : dict, optional
        Settings to modify the default trace type (default: DEFAULT_TRACE_OPTIONS).
    trace_names : str, optional
        Name(s) for the primary trace(s) (default: None).
    trace_name_width : int, optional
        Maximum length of the trace names before text wrapping is used (default: 40).

    Returns
    -------
    plotly.graph_objs.Figure
        The generated Plotly figure.
    """

    def __init__(
        self,
        x,
        y,
        backend=None,
        num_rows=None,
        num_cols=None,
        axis_titles=None,
        trace_options=None,
        trace_names=None,
        trace_name_width=40,
        **kwargs,
    ):
        self.plotter = call_plotting_function(
            "SubplotPlotter",
            backend,
            axis_titles=axis_titles,
            trace_options=trace_options,
            **kwargs,
        )

        self.trace_name_width = trace_name_width

        # Add traces
        if x is not None and y is not None:
            self.add_traces(x, y, trace_names)

        self.num_traces = len(self.plotter.traces)
        self.num_rows = num_rows
        self.num_cols = num_cols
        if self.num_rows is None and self.num_cols is None:
            # Work out the number of subplots
            self.num_cols = int(math.ceil(math.sqrt(self.num_traces)))
            self.num_rows = int(math.ceil(self.num_traces / self.num_cols))
        elif self.num_rows is None:
            self.num_rows = int(math.ceil(self.num_traces / self.num_cols))
        elif self.num_cols is None:
            self.num_cols = int(math.ceil(self.num_traces / self.num_rows))

    def __call__(self, show=True):
        return self.plotter(show=show, num_rows=self.num_rows, num_cols=self.num_cols)


def trajectories(x, y, trace_names=None, show=True, backend=None, **layout_kwargs):
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

    return call_plotting_function(
        "trajectories",
        backend,
        x=x,
        y=y,
        trace_names=trace_names,
        show=show,
        **layout_kwargs,
    )
