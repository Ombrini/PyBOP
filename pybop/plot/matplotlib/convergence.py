from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from pybop.plot.matplotlib.standard_plots import StandardPlot

if TYPE_CHECKING:
    from pybop._result import Result


def convergence(result: "Result", show=True):
    """
    Plot the convergence of the optimisation algorithm.

    Parameters
    -----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).

    Returns
    ---------
    fig : plotly.graph_objs.Figure
        The Plotly figure object for the convergence plot.
    """

    # Extract log from the optimisation object
    cost_log = result.cost_convergence

    # Generate a list of iteration numbers
    iteration_numbers = list(range(1, len(cost_log) + 1))

    # Create a plot dictionary
    plot_dict = StandardPlot(
        x=iteration_numbers,
        y=cost_log,
        trace_names=result.method_name,
    )

    # Generate and display the figure
    fig = plot_dict(show=False)
    plt.xlabel("Evaluation")
    plt.ylabel("Cost")
    plt.title("Convergence")
    plt.tight_layout()

    if show:
        plt.show()

    return fig
