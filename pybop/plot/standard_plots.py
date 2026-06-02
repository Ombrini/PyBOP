import math

from pybop.plot.backends import PlotBackend
from pybop.plot.util import AxisData, get_backend, parse_data, wrap_text


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
    backend: str or pybop.backends.PlotBackend, optional
        Plotting backend to be used to create plot

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
        style: dict = None,
        backend=None,
    ):
        self.lines = []
        self.backend = backend
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.style = style
        if not isinstance(self.backend, PlotBackend):
            self.backend = get_backend(backend)

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
        fig = self.backend.create_figure(
            title=self.title,
            xaxis_title=self.xaxis_title,
            yaxis_title=self.yaxis_title,
            style=self.style,
            traces=self.lines,
        )
        if show:
            self.backend.show_figure(fig)
        else:
            return fig

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
                label = wrap_text(labels[i], 30, backend=self.backend.name)

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
        style: dict = None,
        backend=None,
    ):
        super().__init__(
            x,
            y,
            title=title,
            xaxis_title=xaxis_titles,
            yaxis_title=yaxis_titles,
            labels=labels,
            label_width=label_width,
            style=style,
            backend=backend,
        )

        self.num_lines = len(self.lines)
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

        self.axes_data = []
        for idx in range(self.num_lines):
            row = (idx // self.num_cols) + 1
            col = (idx % self.num_cols) + 1
            self.axes_data.append(AxisData(row, col))

    def __call__(self, show):
        """
        Generate and show the set of figures.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """

        fig, self.axes, self.num_rows, self.num_cols = self.backend.make_subplots(
            self.axes_data,
            title=self.title,
            axis_titles_x=self.xaxis_title,
            axis_titles_y=self.yaxis_title,
            style=self.style,
        )

        for idx, line in enumerate(self.lines):
            row = (idx // self.num_cols) + 1
            col = (idx % self.num_cols) + 1
            self.backend.plot_trace(line, fig, self.axes[(row, col)])

        if show:
            self.backend.show_figure(fig)
        else:
            return fig
