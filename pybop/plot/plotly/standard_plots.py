from pybop.plot import StandardPlot
from pybop.plot.plotly.plotly_manager import PlotlyManager

DEFAULT_LAYOUT_OPTIONS = dict(
    title=None,
    title_x=0.5,
    xaxis=dict(
        title=dict(font={"size": 14}),
        showexponent="last",
        exponentformat="e",
        tickfont=dict(size=12),
    ),
    yaxis=dict(
        title=dict(font={"size": 14}),
        showexponent="last",
        exponentformat="e",
        tickfont=dict(size=12),
    ),
    legend=dict(x=1, y=1, xanchor="right", yanchor="top", font_size=12),
    showlegend=True,
    autosize=False,
    width=600,
    height=600,
    margin=dict(l=10, r=10, b=10, t=75, pad=4),
    plot_bgcolor="white",
)
DEFAULT_SUBPLOT_OPTIONS = dict(
    start_cell="bottom-left",
)
DEFAULT_TRACE_OPTIONS = dict(line=dict(width=4), mode="lines")
DEFAULT_SUBPLOT_TRACE_OPTIONS = dict(line=dict(width=2), mode="lines")


class Plotter:
    """
    A class for creating and displaying interactive Plotly figures.

    Parameters
    ----------
    x : list or np.ndarray, optional
        X-axis data points.
    y : list or np.ndarray, optional
        Primary Y-axis data points for simulated model output.
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
        title=None,
        xaxis_title=None,
        yaxis_title=None,
        layout=None,
        layout_options=None,
        trace_options=None,
    ):
        self.backend = "plotly"

        self.traces = []
        self.layout = layout

        # Set default layout options and update if provided
        if self.layout is None:
            self.layout_options = DEFAULT_LAYOUT_OPTIONS.copy()
            if layout_options:
                self.layout_options.update(layout_options)

        # Set default trace options and update if provided
        self.trace_options = DEFAULT_TRACE_OPTIONS.copy()
        if trace_options:
            self.trace_options.update(trace_options)

        # Attempt to import plotly when an instance is created
        self.go = PlotlyManager().go

        # Create layout
        if self.layout is None:
            self.layout = self.go.Layout(**self.layout_options)

        title_options = {}
        if title is not None:
            title_options.update({"title": title})
        if title is not None:
            title_options.update({"xaxis_title": xaxis_title})
        if title is not None:
            title_options.update({"yaxis_title": yaxis_title})

        self.layout.update(**title_options)

    def __call__(self, show=True):
        """
        Generate and show the figure.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """
        fig = self.go.Figure(data=self.traces, layout=self.layout)
        if show:
            fig.show()

        return fig

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
            if trace_names is not None:
                trace_options["name"] = trace_names[i]
            else:
                trace_options["showlegend"] = False
            trace = self.create_trace(xi, y[i], **trace_options)
            self.traces.append(trace)

    def create_trace(self, x=None, y=None, label=None, **trace_options):
        """
        Create a trace for the Plotly figure.

        Returns
        -------
        plotly.graph_objs.Scatter
            A trace for a Plotly figure.
        """
        if label is not None:
            trace_options.update({"name": label})
        if x is not None and y is not None:
            return self.go.Scatter(
                x=x,
                y=y,
                **trace_options,
            )
        if x is None and y is not None:
            return self.go.Scatter(
                y=y,
                **trace_options,
            )

    def create_fill_trace(self, x, y_upper, y_lower, **options):
        return self.create_trace(
            x=x + x[::-1],
            y=y_upper + y_lower[::-1],
            fill="toself",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=False,
            **options,
        )

    def create_histogram(self, x, name, **trace_options):
        return self.go.Histogram(x=x, name=name, **trace_options)

    def create_vline(self, fig, x, **trace_options):
        fig.add_vline(x=x, **trace_options)


class SubplotPlotter(Plotter):
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
        axis_titles=None,
        layout=None,
        layout_options=DEFAULT_LAYOUT_OPTIONS,
        subplot_options=DEFAULT_SUBPLOT_OPTIONS,
        trace_options=DEFAULT_SUBPLOT_TRACE_OPTIONS,
        **kwargs,
    ):
        super().__init__(layout, layout_options, trace_options, **kwargs)
        self.subplot_options = subplot_options.copy()
        if subplot_options is not None:
            for arg, value in subplot_options.items():
                self.subplot_options[arg] = value

        # Attempt to import plotly when an instance is created
        self.make_subplots = PlotlyManager().make_subplots

        self.axis_titles = axis_titles

    def __call__(self, show=True, num_rows=1, num_cols=1):
        """
        Generate and show the set of figures.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """
        fig = self.make_subplots(
            rows=num_rows,
            cols=num_cols,
            horizontal_spacing=0.1,
            vertical_spacing=0.15,
            **self.subplot_options,
        )
        fig.update_layout(self.layout_options)

        for idx, trace in enumerate(self.traces):
            row = (idx // num_cols) + 1
            col = (idx % num_cols) + 1
            fig.add_trace(trace, row=row, col=col)

            if self.axis_titles and idx < len(self.axis_titles):
                x_title, y_title = self.axis_titles[idx]
                fig.update_xaxes(title_text=x_title, row=row, col=col)
                fig.update_yaxes(
                    title_text=y_title,
                    row=row,
                    col=col,
                    showexponent="last",
                    exponentformat="e",
                )

        if show:
            fig.show()

        return fig


def trajectories(x, y, trace_names=None, show=True, **layout_kwargs):
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
    # Create a plot dictionary
    plot_dict = StandardPlot(x=x, y=y, trace_names=trace_names, backend="plotly")

    # Generate the figure and update the layout
    fig = plot_dict(show=False)
    fig.update_layout(**layout_kwargs)
    if show:
        fig.show()

    return fig


def show_table(header, values, title):
    """
    Display data in a table.
    """
    # Import plotly only when needed
    go = PlotlyManager().go
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=header),
                cells=dict(
                    values=[[row[0] for row in values], [row[1] for row in values]]
                ),
            )
        ]
    )

    fig.update_layout(title=title)
    fig.show()
