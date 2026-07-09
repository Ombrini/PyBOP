import math

import numpy as np

from pybop.plot.util import get_backend_from_figure, parse_data, wrap_text


class StandardPlot:
    """
    A class for creating and displaying figures.

    Parameters
    ----------
    x : list or np.ndarray, optional
        X-axis data points.
    y : list or np.ndarray, optional
        Primary Y-axis data points for simulated model output.
    title: str, optional
        The title of the figure
    xaxis_title: str, optional
        Sets the title/label of the x-axis
    yaxis_title: str, optional
        Sets the title/label of the y-axis
        Settings to modify the default trace type (default: DEFAULT_TRACE_OPTIONS).
    labels : str, optional
        Name(s) for the primary trace(s) (default: None).
    label_width : int, optional
        Maximum length of the labels before text wrapping is used (default: 40).
    style: dict, optional
    legend_style: dict, optional
    backend: str or pybop.backends.PlotBackend, optional
        Plotting backend to be used to create plot
    figures: figure object, optional
        Figure for plotting. If not provided a new figure is created
    axes: axis, optional
        Thes axis to be used for plotting
        plotly: axis expected to be of the form tuple(row, col)

    Returns
    -------
    plotly.graph_objs.Figure or matplotlib.figure.Figure
        The generated Plotly figure.
    """

    def __init__(
        self,
        x,
        y,
        title: str = None,
        xaxis_title: str = None,
        yaxis_title: str = None,
        labels: list[str] = None,
        label_width=40,
        text_wrap_width=None,
        style: dict = None,
        legend_style: dict = None,
        backend=None,
        figures=None,
        axes=None,
    ):
        self.lines = []
        self.backend = get_backend_from_figure(backend, figures)
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.style = style
        self.legend_style = legend_style
        self.fig = np.atleast_1d(figures)[0]
        self.text_wrap_width = text_wrap_width
        _, axes, _, _ = self.backend.parse_input_axes(self.fig, axes, num_plots=1)
        self.ax = axes[0]

        if x is not None and y is not None:
            self.add_lines(x, y, labels, label_width)

    def __call__(self, show=True):
        """
        Generate and show the figure.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """
        if self.fig is None:
            self.fig = self.backend.create_figure(style=self.style)
            self.ax = None

        self.backend.update_axes_titles(
            self.fig, self.ax, self.xaxis_title, self.yaxis_title
        )
        self.backend.update_plot_titles(self.fig, self.ax, self.title)
        for line in self.lines:
            self.backend.plot_trace(line, fig=self.fig, ax=self.ax)
        if self.legend_style is not None:
            self.backend.legend(self.fig, style=self.legend_style, axes=self.ax)

        if show:
            self.backend.show_figure(self.fig)
        else:
            return self.fig

    def add_lines(self, x, y, labels=None, labelwidth=40):
        """
        Add a set of lines.

        Parameters
        ----------
        x : list or np.ndarray
            X-axis data points.
        y : list or np.ndarray
            Primary Y-axis data points for simulated model output.
        labels : str or list[str], optional
            Name(s) for the primary line(s) (default: None).
        label_width : int, optional
            Maximum length of the labels before text wrapping is used (default: 40).
        """
        # Parse the data
        x, y = parse_data(x, y)
        xi = x[0]
        for i in range(0, len(y)):
            if len(x) > 1:
                xi = x[i]
            label = None
            if labels is not None:
                label = wrap_text(labels[i], labelwidth, backend=self.backend.name)

            line = self.backend.line(xi, y[i], label)
            self.lines.append(line)


class StandardSubplot(StandardPlot):
    """
    A class for creating and displaying a set of figures in a grid layout.

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
    title: str, optional
        Title of the Figure
    xaxis_titles: str or list of str, optional
        titles for the x-axes (default: None)
    yaxis_titles: str or list of str, optional
        titles for the x-axes (default: None)

    labels : str, optional
        Name(s) for the primary trace(s) (default: None).
    label_width : int, optional
        Maximum length of the trace names before text wrapping is used (default: 40).
    style: dict, optional
        Options for figure layout
    backend: str or pybop.plot.backends.PlotBackend
    figures: figure object, optional
        Figure for plotting. If not provided a new figure is created
    axes: axis, optional
        Thes axis to be used for plotting
        plotly: axis expected to be of the form tuple(row, col)

    Returns
    -------
    plotly.graph_objs.Figure or matplotlib.figure.Figure
        The generated figure.
    """

    def __init__(
        self,
        x,
        y,
        num_rows: int = None,
        num_cols: int = None,
        title: str = None,
        xaxis_titles: list[str] | str = None,
        yaxis_titles: list[str] | str = None,
        labels: list[str] = None,
        label_width: int = 40,
        text_wrap_width: int = None,
        style: dict = None,
        backend=None,
        figures=None,
        axes=None,
    ):
        super().__init__(
            x,
            y,
            title=title,
            xaxis_title=xaxis_titles,
            yaxis_title=yaxis_titles,
            labels=labels,
            label_width=label_width,
            text_wrap_width=text_wrap_width,
            style=style,
            backend=backend,
            figures=figures,
        )
        self.num_lines = len(self.lines)
        self.compute_ax = False
        self.num_rows = None
        self.num_cols = None

        if self.fig is not None:
            _, self.axes, _, _ = backend.parse_input_axes(
                self.fig, axes, num_plots=self.num_lines
            )
        else:
            self.num_rows = num_rows
            self.num_cols = num_cols
            if self.num_rows is None and self.num_cols is None:
                # Work out the number of subplots
                self.num_cols = int(math.ceil(math.sqrt(self.num_lines)))
                self.num_rows = int(math.ceil(self.num_lines / self.num_cols))
            elif self.num_rows is None:
                self.num_rows = int(math.ceil(self.num_lines / self.num_cols))
            elif self.num_cols is None:
                self.num_cols = int(math.ceil(self.num_lines / self.num_rows))

    def __call__(self, show):
        """
        Generate and show the set of figures.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """
        if self.fig is None:
            self.fig, self.axes = self.backend.make_subplots(
                self.num_rows,
                self.num_cols,
                num_plots=self.num_lines,
                style=self.style,
            )

        # Reduce wrapping width as the number of subplot rows increases.
        width = self.text_wrap_width or np.floor(
            50 / (self.num_rows or np.ceil(np.sqrt(self.num_lines)))
        )
        self.backend.update_axes_titles(
            self.fig, self.axes, self.xaxis_title, self.yaxis_title, max_width=width
        )
        # Reduce wrapping width as the number of subplot cols increases.
        width = self.text_wrap_width or np.floor(
            50 / (self.num_cols or np.ceil(np.sqrt(self.num_lines)))
        )
        self.backend.update_plot_titles(
            self.fig, self.axes, self.title, max_text_width=width
        )

        for idx, line in enumerate(self.lines):
            ax = self.axes[idx % len(self.axes)]
            self.backend.plot_trace(line, self.fig, ax=ax)

        if show:
            self.backend.show_figure(self.fig)
        else:
            return self.fig
