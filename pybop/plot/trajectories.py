from pybop.plot.util import (
    get_backend,
    wrap_text,
    parse_data
)


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

    backend = get_backend(backend)
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

        backend.plot_trace(backend.line(xi, y[i], label), fig)
    
    backend.legend(fig)

    if show:
        backend.show_figure(fig)
    return fig