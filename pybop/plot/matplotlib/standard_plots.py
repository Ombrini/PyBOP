import warnings

from matplotlib import pyplot as plt

from pybop.plot import StandardPlot

DEFAULT_TRACE_OPTIONS = dict(linewidth=2.0)


class Plotter:
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
        trace_options=None,
        figsize=(8, 6),
        **kwargs,
    ):
        self.backend = "matplotlib"
        # Warning if layout arguments ignored
        if len(kwargs) > 0:
            warnings.warn(
                "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
                f"{list(kwargs.keys())}",
                UserWarning,
                stacklevel=2,
            )

        # Set default trace options and update if provided
        self.trace_options = DEFAULT_TRACE_OPTIONS.copy()
        if trace_options:
            self.trace_options.update(trace_options)

        self.fig = plt.figure(figsize=figsize, dpi=100)
        self.traces = []

    def __call__(self, show=True):
        """
        Generate and show the figure.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """
        # Add traces
        for trace in self.traces:
            self._plot_trace(**trace)

        plt.tick_params(axis="both", labelsize=12)
        plt.ticklabel_format(axis="both", style="sci", scilimits=(-4, 4))

        labels_in_fig = True
        for ax in self.fig.axes:
            if not ax.get_legend_handles_labels() == ([], []):
                break
        else:
            labels_in_fig = False
        if labels_in_fig:
            plt.legend(
                **dict(loc="best", fontsize=12),
            )

        if show:
            plt.show()
        else:
            return self.fig

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

    def create_trace(self, x, y, label, ax=None, **trace_options):
        """
        Add line to plot.

        Returns
        -------
        plotly.graph_objs.Scatter
            A trace for a Plotly figure.
        """
        size = min(len(x), len(y))
        trace = dict(x=x[:size], y=y[:size], label=label, ax=ax)
        trace.update(trace_options)
        return trace

    def _plot_trace(self, x, y, label, ax=None, **trace_options):
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
        trace_options=DEFAULT_TRACE_OPTIONS,
        figsize=(8, 6),
        **kwargs,
    ):
        super().__init__(trace_options, figsize, **kwargs)
        self.axis_titles = axis_titles

    def __call__(self, show=True, num_rows=1, num_cols=1):
        """
        Generate and show the set of figures.

        Parameters
        ----------
        show : bool, optional
            If True, the figure is shown upon creation (default: True).
        """

        color_cycle = plt.rcParams["axes.prop_cycle"]()

        lines = []
        show_legend = False
        for idx, trace in enumerate(self.traces):
            ax = self.fig.add_subplot(num_rows, num_cols, idx + 1)
            trace["ax"] = ax
            if self.axis_titles and idx < len(self.axis_titles):
                x_title, y_title = self.axis_titles[idx]
                ax.set_xlabel(x_title)
                ax.set_ylabel(y_title)
            if "label" in trace.keys() and trace["label"] is not None:
                show_legend = True

            lines.append(self._plot_trace(**trace, **next(color_cycle)))

        lines_labels = [ax.get_legend_handles_labels() for ax in self.fig.axes]
        lines, labels = [sum(lol, []) for lol in zip(*lines_labels, strict=False)]
        if show_legend:
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
    plot_dict = StandardPlot(x=x, y=y, trace_names=trace_names, backend="matplotlib")

    # Generate the figure and update the layout
    fig = plot_dict(show=False)
    plt.title(title)
    plt.xlabel(xaxis_title, fontsize=12)
    plt.ylabel(yaxis_title, fontsize=12)
    plt.tight_layout()
    if show:
        fig.show()

    return fig
