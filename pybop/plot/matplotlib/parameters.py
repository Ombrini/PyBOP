import warnings
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from pybop.costs.log_likelihoods import GaussianLogLikelihood
from pybop.plot.standard_plots import StandardSubplot

if TYPE_CHECKING:
    from pybop._result import Result


def parameters(result: "Result", show=True, **layout_kwargs):
    """
    Plot the evolution of parameters during the optimisation process using Plotly.

    Parameters
    ----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).

    Returns
    -------
    plotly.graph_objs.Figure
        A Plotly figure object showing the parameter evolution over iterations.
    """

    if len(layout_kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(layout_kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )

    # Extract parameters and log from the optimisation object
    parameters = result.problem.parameters
    x = list(range(len(result.x_model)))
    y = [list(item) for item in zip(*result.x_model, strict=False)]

    # Create lists of axis titles and trace names
    axis_titles = []
    trace_names = parameters.names
    for name in trace_names:
        axis_titles.append(("Evaluation", name))

    if isinstance(result.problem, GaussianLogLikelihood):
        axis_titles.append(("Evaluation", "Sigma"))
        trace_names.append("Sigma")

    # Create a plot dictionary
    plot_dict = StandardSubplot(
        x=x,
        y=y,
        axis_titles=axis_titles,
        trace_names=trace_names,
        trace_name_width=50,
        figsize=(18, 8),
        backend="matplotlib",
    )

    plt.suptitle("Parameter Convergence")

    # Generate the figure and update the layout
    fig = plot_dict(show=False)
    if show:
        plt.show()

    return fig
