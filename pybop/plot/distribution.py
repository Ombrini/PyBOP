import numpy as np

from pybop.parameters.parameter import Parameters
from pybop.plot.standard_plots import Subplots
from pybop.plot.util import import_backend


def distribution(
    parameters: Parameters,
    posterior: Parameters | None = None,
    n_samples: int = 100,
    transformed: bool = False,
    show: bool = True,
    backend = None,
):
    """
    Plot the posterior on top of the prior distribution for a Bayesian optimisation result.
    """
    # Create lists of axis titles and trace names
    axis_titles_x = []
    axis_titles_y = []
    trace_names = (
        parameters.names
        if posterior is None
        else ["Prior"] * len(parameters)
    )
    for name in parameters.names:
        axis_titles_x.append(
            name + " (transformed)" if transformed else name
        )
        axis_titles_y.append("Probability density")

    # Evaluate marginal distributions for each parameter
    values = []
    probability = []
    for p in parameters:
        d = p.transformed_distribution if transformed else p.distribution
        samples = d.rvs(size=n_samples)
        parameter_range = np.linspace(min(samples), max(samples), n_samples)
        values.append(parameter_range)
        probability.append([d.pdf(s) for s in values[-1]])

    # Create a plot dictionary
    subplots = Subplots(       
        x=values,
        y=probability,
        backend=backend
    )

    subplots.create_figure(
        axis_titles_x=axis_titles_x, 
        axis_titles_y=axis_titles_y,
        style={
            "width" : 1024,
            "height" : 576
        }
    )

    subplots.plot_lines(
        labels=trace_names
    )
 
    backend = import_backend(backend)

    if posterior is not None:
        for idx, p in enumerate(posterior):
            d = p.transformed_distribution if transformed else p.distribution
            samples = d.rvs(size=n_samples)
            parameter_range = np.linspace(min(samples), max(samples), n_samples)
            values.append(parameter_range)
            probability.append([d.pdf(s) for s in values[-1]])

            trace = backend.line_plot(
                values[-1], probability[-1], label="Posterior"
            )
            row = (idx // subplots.num_cols) + 1
            col = (idx % subplots.num_cols) + 1
            backend.plot_trace(trace, subplots.fig, ax=subplots.get_axis(row, col))
    backend.legend(subplots.fig, style=dict(horizontal=True, loc="lower right", coords=(1, 1.02)),)
    if show:
        backend.show_figure(subplots.fig)

    return subplots.fig
