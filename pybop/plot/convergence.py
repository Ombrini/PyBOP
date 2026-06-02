from typing import TYPE_CHECKING

from pybop.plot.util import get_backend

if TYPE_CHECKING:
    from pybop._result import Result


def convergence(result: "Result", show: bool = True, backend: str = None):
    """
    Plot the convergence of the optimisation algorithm.

    Parameters
    -----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    backend : str, optional
        Select a plotting backend. If None, the current default backend is used.

    Returns
    ---------
    fig : plotly.graph_objs.Figure or matplotlib.figure.Figure
        The figure object for the convergence plot.
    """

    # Extract log from the optimisation object
    cost_log = result.cost_convergence

    # Generate a list of iteration numbers
    iteration_numbers = list(range(1, len(cost_log) + 1))

    backend = get_backend(backend)

    # Create figure
    fig = backend.create_figure(
        xaxis_title="Evaluation",
        yaxis_title="Cost",
        title="Convergence",
        style={"bg_color": "white", "width": 600, "height": 600},
    )

    # Add line plot
    backend.plot_trace(
        backend.line(
            x=iteration_numbers,
            y=cost_log,
            label=result.method_name,
        ),
        fig,
    )

    # Display or return figure
    if show:
        backend.show_figure(fig)
    else:
        return fig
