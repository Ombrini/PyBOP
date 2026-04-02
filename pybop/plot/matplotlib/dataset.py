import matplotlib.pyplot as plt

from pybop.plot.matplotlib.standard_plots import StandardPlot, trajectories


def dataset(dataset, signal=None, trace_names=None, show=True):
    """
    Quickly plot a PyBOP Dataset using Plotly.

    Parameters
    ----------
    dataset : object
        A PyBOP dataset.
    signal : list or str, optional
        The name of the time series to plot (default: "Voltage [V]").
    trace_names : list or str, optional
        Name(s) for the trace(s) (default: "Data").
    show : bool, optional
        If True, the figure is shown upon creation (default: True).

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object for the scatter plot.
    """

    # Get data dictionary
    if signal is None:
        signal = ["Voltage [V]"]
    dataset.check(signal=signal)

    # Compile ydata and labels or legend
    y = [dataset[s] for s in signal]
    if len(signal) == 1:
        yaxis_title = signal[0]
        if trace_names is None:
            trace_names = ["Data"]
    else:
        yaxis_title = "Output"
        if trace_names is None:
            trace_names = StandardPlot.remove_brackets(signal)

    # Create the figure
    fig = trajectories(
        x=dataset[dataset.domain],
        y=y,
        trace_names=trace_names,
        show=False,
        xaxis_title=StandardPlot.remove_brackets(dataset.domain),
        yaxis_title=yaxis_title,
    )
    if show:
        plt.show()

    return fig
