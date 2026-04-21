from copy import deepcopy

from pybop.plot import StandardPlot
from pybop.plot.plotly.plotly_manager import PlotlyManager


def plot_trace(trace, fig, ax=None):
    if ax is None:
        fig.add_trace(trace)
    else:
        fig.add_trace(trace, row=ax.row, col=ax.col)
        fig.update_xaxes(title_text=ax.xlabel, row=ax.row, col=ax.col)
        fig.update_yaxes(title_text=ax.ylabel, row=ax.row, col=ax.col)


def add_traces(x, y, trace_names, **trace_options):
    traces = []
    xi = x[0]
    for i in range(0, len(y)):
        opts = deepcopy(trace_options)
        if len(x) > 1:
            xi = x[i]
        label = None
        if trace_names is not None:
            label = trace_names[i]

        traces.append(line_plot(xi, y[i], label, **opts))
    return traces


def line_plot(x=None, y=None, label=None, ax=None, **kwargs):
    go = PlotlyManager().go
    if label is not None:
        kwargs.update({"name": label})
    if x is not None and y is not None:
        return go.Scatter(
            x=x,
            y=y,
            **kwargs,
        )
    if x is None and y is not None:
        return go.Scatter(
            y=y,
            **kwargs,
        )


def contour_plot(x, y, z, **kwargs):
    go = PlotlyManager().go
    return go.Contour(x=x, y=y, z=z, **kwargs)


def fill_plot(x, y_upper, y_lower, **options):
    return line_plot(
        x=x + x[::-1],
        y=y_upper + y_lower[::-1],
        fill="toself",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=False,
        **options,
    )


def histogram_plot(x, name, **trace_options):
    go = PlotlyManager().go
    return go.Histogram(x=x, name=name, **trace_options)


def add_vline(fig, x, **trace_options):
    fig.add_vline(x=x, **trace_options)


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


def plot_optimisation_path(plot_dict: StandardPlot, x, y):
    plot_dict.traces.append(
        plot_dict.create_trace(
            x,
            y,
            mode="markers",
            marker=dict(
                color=[i / len(x) for i in range(len(x))],
                colorscale="Greys",
                size=8,
                showscale=False,
            ),
            showlegend=False,
        )
    )
