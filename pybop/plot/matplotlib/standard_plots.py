import math
import textwrap
import warnings

import numpy as np
from matplotlib import pyplot as plt

DEFAULT_TRACE_OPTIONS = dict(linewidth=2.0)


class StandardPlot:
    """
    A class for creating and displaying interactive Plotly figures.

    Parameters
    ----------
    x : list or np.ndarray, optional
        X-axis data points.
    y : list or np.ndarray, optional
        Primary Y-axis data points for simulated model output.
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
        x=None,
        y=None,
        trace_options=None,
        trace_names=None,
        trace_name_width=20,
        figsize=(8, 6),
        **kwargs,
    ):
        # Warning if layout arguments ignored
        if len(kwargs) > 0:
            warnings.warn(
                "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
                f"{list(kwargs.keys())}",
                UserWarning,
                stacklevel=2,
            )
        self.traces = []
        self.trace_name_width = trace_name_width

        # Set default trace options and update if provided
        self.trace_options = DEFAULT_TRACE_OPTIONS.copy()
        if trace_options:
            self.trace_options.update(trace_options)

        # Parse the data
        x, y = self.parse_data(x, y)
        self.x = x
        self.y = y
        # Check and wrap trace names
        if trace_names is not None:
            if isinstance(trace_names, str):
                trace_names = [trace_names]
            for i, name in enumerate(trace_names):
                trace_names[i] = self.wrap_text(name, width=self.trace_name_width)
        self.trace_names = trace_names

        self.fig = plt.figure(figsize=figsize, dpi=100)

    def __call__(self, show=True):
        """
        Generate and show the figure.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """
        # Add traces
        if self.x is not None and self.y is not None:
            self.add_traces(self.x, self.y, self.trace_names)
        self.default_layout()
        if show:
            plt.show()

        return self.fig

    def default_layout(self):

        plt.tick_params(axis="both", labelsize=12)
        plt.ticklabel_format(axis="both", style="sci", scilimits=(-4, 4))

    def add_traces(self, x, y, trace_names=None, **trace_options):
        """
        Add a set of traces to the plot dictionary.

        Parameters
        ----------
        x : list or np.ndarray
            X-axis data points.
        y : list or np.ndarray
            Primary Y-axis data points for simulated model output.
        trace_names : str or list[str], optional
            Name(s) for the primary trace(s) (default: None).
        """

        options = self.trace_options.copy()
        options.update(trace_options)

        # Create a trace for each trajectory
        xi = x[0]
        for i in range(0, len(y)):
            trace_options = options.copy()
            if len(x) > 1:
                xi = x[i]

            label = None
            if trace_names is not None:
                label = trace_names[i]

            self.traces.append(self.create_trace(xi, y[i], label, **trace_options))

        if self.trace_names is not None:
            plt.legend(
                **dict(loc="best", fontsize=12),
            )

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
        if x is None or y is None:
            return None, None
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

    def create_trace(self, x, y, label, ax=None, **trace_options):
        """
        Create a trace for the Plotly figure.

        Returns
        -------
        plotly.graph_objs.Scatter
            A trace for a Plotly figure.
        """

        if ax is None:
            ax = plt.gca()

        line = ax.plot(
            x,
            y,
            label=label,
            **trace_options,
        )
        if len(line) > 1:
            return line
        else:
            return line[0]

    @staticmethod
    def wrap_text(text, width):
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
        num_rows=None,
        num_cols=None,
        axis_titles=None,
        trace_options=DEFAULT_TRACE_OPTIONS,
        trace_names=None,
        trace_name_width=40,
        figsize=(8, 6),
    ):
        super().__init__(x, y, trace_options, trace_names, trace_name_width, figsize)
        self.num_traces = len(self.y)
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
        self.axis_titles = axis_titles

    def __call__(self, show):
        """
        Generate and show the set of figures.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """

        color_cycle = plt.rcParams["axes.prop_cycle"]()

        xi = self.x[0]
        lines = []
        for idx, yi in enumerate(self.y):
            ax = self.fig.add_subplot(self.num_rows, self.num_cols, idx + 1)
            if self.axis_titles and idx < len(self.axis_titles):
                x_title, y_title = self.axis_titles[idx]
                ax.set_xlabel(x_title)
                ax.set_ylabel(y_title)
            if len(self.x) > 1:
                xi = self.x[idx]

            label = None
            if self.trace_names is not None:
                label = self.trace_names[idx]

            lines.append(self.create_trace(xi, yi, label, ax=ax, **next(color_cycle)))

        lines_labels = [ax.get_legend_handles_labels() for ax in self.fig.axes]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        if self.trace_names is not None:
            self.fig.legend(
                lines,
                labels,
                loc="upper right",
                ncol=len(lines),
                bbox_to_anchor=(0.99, 0.95),
            )
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        if show:
            plt.show()

        return self.fig


def trajectories(
    x,
    y,
    trace_names=None,
    show=True,
    xaxis_title="",
    yaxis_title="",
    title="",
    **layout_kwargs,
):
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
            This argument is ignored for the matplotlib backend.
            Valid Plotly layout keys and their values,
            e.g. `xaxis_title="Time / s"` or
            `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """

    if len(layout_kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(layout_kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )
    # Create a plot dictionary
    plot_dict = StandardPlot(
        x=x,
        y=y,
        trace_names=trace_names,
    )

    # Generate the figure and update the layout
    fig = plot_dict(show=False)
    plt.title(title)
    plt.xlabel(xaxis_title, fontsize=12)
    plt.ylabel(yaxis_title, fontsize=12)
    plt.tight_layout()
    if show:
        plt.show()

    return plot_dict
