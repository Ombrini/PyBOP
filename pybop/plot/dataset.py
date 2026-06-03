from pybop.plot.trajectories import trajectories
from pybop.plot.util import get_backend, remove_brackets


def dataset(dataset, signal=None, labels=None, show=True, backend=None):
    """
    Quickly plot a PyBOP Dataset using Plotly.

    Parameters
    ----------
    dataset : object
        A PyBOP dataset.
    signal : list or str, optional
        The name of the time series to plot (default: "Voltage [V]").
    labels : list or str, optional
        Name(s) for the trace(s) (default: "Data").
    show : bool, optional
        If True, the figure is shown upon creation (default: True).

    Returns
    -------
    fig : plotly.graph_objs.Figure or matplotlib.figure.Figure
        The figure object for the scatter plot.
    """

    # Get data dictionary
    if signal is None:
        signal = ["Voltage [V]"]
    dataset.check(signal=signal)

    # Compile ydata and labels or legend
    y = [dataset[s] for s in signal]
    if len(signal) == 1:
        yaxis_title = remove_brackets(signal[0])
        if labels is None:
            labels = ["Data"]
    else:
        yaxis_title = "Output"
        if labels is None:
            labels = remove_brackets(signal)

    # Create the figure
    fig = trajectories(
        x=dataset[dataset.domain],
        y=y,
        labels=labels,
        show=False,
        xaxis_title=remove_brackets(dataset.domain),
        yaxis_title=yaxis_title,
        backend=backend,
    )

    backend_module = get_backend(backend)
    if show:
        backend_module.show_figure(fig)

    return fig
