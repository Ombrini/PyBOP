import warnings
from copy import deepcopy

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt

from pybop.plot import StandardPlot


def add_traces(x, y, trace_names, **trace_options):
    color_cycle = None
    if trace_options.get("use_color_cycle"):
        color_cycle = plt.rcParams["axes.prop_cycle"]()
        del trace_options["use_color_cycle"]
    traces = []
    xi = x[0]
    for i in range(0, len(y)):
        if len(x) > 1:
            xi = x[i]
        label = None
        if trace_names is not None:
            label = trace_names[i]
        if color_cycle is not None:
            traces.append(
                line_plot(xi, y[i], label, **trace_options, **next(color_cycle))
            )
        else:
            traces.append(line_plot(xi, y[i], label, **trace_options))

    return traces


def plot_trace(trace: dict, fig, ax=None, color_cycle=None):
    # retrieve axis, plot_type and positional arguments
    plot_type = trace.get("plot_type") or "plot"
    positional_args = trace.get("positional_args") or None
    ax = ax or fig.gca()

    # axis titles
    if "xaxis_title" in trace.keys():
        ax.set_xlabel(trace["xaxis_title"])
    if "yaxis_title" in trace.keys():
        ax.set_ylabel(trace["yaxis_title"])

    # retrieve remaining arguments
    trace_options = deepcopy(trace)
    for key in ["plot_type", "positional_args", "xaxis_title", "yaxis_title"]:
        if key in trace_options.keys():
            del trace_options[key]

    # update color
    if color_cycle is not None and plot_type == "plot":
        trace_options.update(**next(color_cycle))

    # get plotting function
    try:
        plot_function = getattr(ax, plot_type)
    except ValueError:
        print("Plot type not recognised")

    obj = plot_function(*positional_args, **trace_options)
    if plot_type == "contourf":
        plt.colorbar(obj)

    return obj


def line_plot(x=None, y=None, label=None, **kwargs):
    if x is not None and y is not None:
        size = min(len(x), len(y))
        trace = dict(positional_args=[x[:size], y[:size]], label=label)
    elif y is not None:
        trace = dict(positional_args=[y], label=label)

    trace.update(kwargs)
    return trace


def colorbar(fig, data, colorscale="viridis", label=None):
    # normalise cost
    f_min = np.nanmin(data[np.isfinite(data)])
    f_max = np.nanmax(data[np.isfinite(data)])
    norm = mpl.colors.Normalize(vmin=f_min, vmax=f_max, clip=True)

    # get colours
    cmap = mpl.colormaps["viridis"]

    plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=fig.gca(), label=label)


def contour_plot(x, y, z, **kwargs):
    contour = dict(positional_args=[x, y, z], plot_type="contourf")
    contour.update(**kwargs)
    contour_lines = dict(
        positional_args=[x, y, z],
        colors=("k"),
        linestyles="solid",
        linewidths=0.2,
        plot_type="contour",
    )
    return contour, contour_lines


def scatter_plot(x, y, colors=None, labels=None, **trace_options):
    scatter = dict(positional_args=[x, y], plot_type="scatter")
    scatter.update(**trace_options)
    if colors is not None:
        scatter["c"] = colors
    return scatter


def fill_between_plot(x, y_upper, y_lower, **options):
    trace = dict(positional_args=(x, y_upper, y_lower), plot_type="fill_between")
    trace.update(options)
    return trace


def fill_plot(x, y, color=None, label=None):
    return dict(positional_args=(x, y), plot_type="fill", color=color)


def histogram_plot(x, name, **trace_options):
    trace = dict(positional_args=[x], label=name, plot_type="hist")
    trace.update(trace_options)
    return trace


def add_vline(fig, x, **trace_options):
    fig.gca()
    plt.axvline(x, **trace_options)


def sample_color_scale(data, scale="viridis", d_min=None, d_max=None):
    # normalise and clip data
    d_min = d_min or np.nanmin(data[np.isfinite(data)])
    d_max = d_max or np.nanmax(data[np.isfinite(data)])
    norm = mpl.colors.Normalize(vmin=d_min, vmax=d_max, clip=True)
    norm_d = norm(data, clip=True)
    if np.isscalar(norm_d):
        norm_d = [norm_d]

    # get colours
    cmap = mpl.colormaps[scale]
    return cmap(norm_d)


def show_table(header, values, title):
    """
    Display data in a table.
    """
    for i, val in enumerate(values):
        values[i] = [val[0], ", ".join(val[1].astype(str))]

    fig, ax = plt.subplots(figsize=(6, 2), dpi=100)

    # hide axes
    ax.axis("off")
    ax.axis("tight")
    ax.table(
        cellText=values,
        colLabels=header,
        loc="center",
        cellLoc="center",
        colColours=["lightsteelblue", "lightsteelblue"],
    )
    ax.set_title(title)
    fig.tight_layout()
    plt.show()


def plot_optimisation_path(plot_dict: StandardPlot, x, y):
    plot_dict.traces.append(
        scatter_plot(
            x,
            y,
            c=[i / len(x) for i in range(len(x))],
            cmap="Grays",
            zorder=1,
        )
    )


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
