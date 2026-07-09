from pybop.plot.standard_plots import StandardPlot


def trajectories(
    x,
    y,
    title: str = None,
    xaxis_title: str = None,
    yaxis_title: str = None,
    labels=None,
    label_width=20,
    show=True,
    backend=None,
    figures=None,
    axes=None,
):
    """
    Quickly plot one or more trajectories using Plotly.

    Parameters
    ----------
    x : list or np.ndarray
        X-axis data points.
    y : list or np.ndarray
        Y-axis data points for each trajectory.
    title: str, optional
        The title of the figure
    xaxis_title: str, optional
        Sets the title/label of the x-axis
    yaxis_title: str, optional
        Sets the title/label of the y-axis
        Settings to modify the default trace type (default: DEFAULT_TRACE_OPTIONS).
    labels : list or str, optional
        Name(s) for the trace(s) (default: None).
    label_width : int, optional
        Maximum length of the labels before text wrapping is used (default: 20).
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    backend: str, optional
        The plotting backend to be used.
    figures: figure object, optional
        Figure for plotting. If not provided a new figure is created
    axes: axis, optional
        Thes axis to be used for plotting
        plotly: axis expected to be of the form tuple(row, col)

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """
    plot_dict = StandardPlot(
        x,
        y,
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        labels=labels,
        label_width=label_width,
        style={"height": 600, "width": 600, "bg_color": "white"},
        legend_style={},
        backend=backend,
        figures=figures,
        axes=axes,
    )

    fig = plot_dict(show=show)

    return fig
