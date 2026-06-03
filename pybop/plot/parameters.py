from typing import TYPE_CHECKING

from pybop.costs.log_likelihoods import GaussianLogLikelihood
from pybop.plot.standard_plots import StandardSubplot
from pybop.plot.util import get_backend

if TYPE_CHECKING:
    from pybop._result import Result


def parameters(result: "Result", show: bool = True, backend: str = None):
    """
    Plot the evolution of parameters during the optimisation process using Plotly.

    Parameters
    ----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    backend: str, optional
        The plotting backend to be used

    Returns
    -------
    plotly.graph_objs.Figure or matplotlib.figure.Figure
        A figure object showing the parameter evolution over iterations.
    """

    # Extract parameters and log from the optimisation object
    parameters = result.problem.parameters
    x = list(range(len(result.x_model)))
    y = [list(item) for item in zip(*result.x_model, strict=False)]

    # Create lists of axis titles and trace names
    xaxis_titles = []
    yaxis_titles = []
    labels = parameters.names
    if isinstance(result.problem, GaussianLogLikelihood):
        labels.append("Sigma")

    for name in labels:
        xaxis_titles.append("Evaluation")
        yaxis_titles.append(name)

    # import plotting backend
    backend = get_backend(backend)

    # Create a plot dictionary
    plot_dict = StandardSubplot(
        x,
        y,
        title="Parameter Convergence",
        xaxis_titles=xaxis_titles,
        yaxis_titles=yaxis_titles,
        style=dict(bg_color="white", width=1600, height=800),
        labels=labels,
        backend=backend,
    )

    fig = plot_dict(show=False)

    # add legend
    backend.legend(
        fig,
        style={
            "fig_legend": True,
            "outside": ("right", 0.18),
        },
    )

    # Generate the figure and update the layout
    if show:
        backend.show_figure(fig)

    return fig
