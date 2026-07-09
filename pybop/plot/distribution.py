import numpy as np

from pybop.parameters.parameter import Parameters
from pybop.plot.standard_plots import StandardSubplot
from pybop.plot.util import get_backend_from_figure


def distribution(
    parameters: Parameters,
    posterior: Parameters | None = None,
    n_samples: int = 100,
    transformed: bool = False,
    show: bool = True,
    backend: str = None,
    figures=None,
    axes=None,
):
    """
    Plot the posterior on top of the prior distribution for a Bayesian optimisation result.
    """

    # Create lists of axis titles and trace names
    xaxis_titles = []
    yaxis_titles = []
    labels = parameters.names if posterior is None else ["Prior"] * len(parameters)
    for name in parameters.names:
        xaxis_titles.append(name + " (transformed)" if transformed else name)
        yaxis_titles.append("Probability density")

    # Evaluate marginal distributions for each parameter
    values = []
    probability = []
    for p in parameters:
        d = p.transformed_distribution if transformed else p.distribution
        samples = d.rvs(size=n_samples)
        parameter_range = np.linspace(min(samples), max(samples), n_samples)
        values.append(parameter_range)
        probability.append([d.pdf(s) for s in values[-1]])

    # Get plotting backend
    backend = get_backend_from_figure(backend, figures)

    # Create a plot dictionary
    plot_dict = StandardSubplot(
        x=values,
        y=probability,
        xaxis_titles=xaxis_titles,
        yaxis_titles=yaxis_titles,
        labels=labels,
        style={"width": 1024, "height": 576},
        backend=backend,
        figures=figures,
        axes=axes,
    )

    fig = plot_dict(show=False)

    if posterior is not None:
        for idx, p in enumerate(posterior):
            d = p.transformed_distribution if transformed else p.distribution
            samples = d.rvs(size=n_samples)
            parameter_range = np.linspace(min(samples), max(samples), n_samples)
            values.append(parameter_range)
            probability.append([d.pdf(s) for s in values[-1]])

            line = backend.line(values[-1], probability[-1], label="Posterior")
            ax = plot_dict.axes[idx % len(plot_dict.axes)]
            backend.plot_trace(line, fig, ax=ax)

    for ax in plot_dict.axes:
        backend.legend(
            fig,
            style=dict(
                horizontal=True,
                outside=("top", 0.1),
                loc="lower right",
                coords=(1, 1.02),
                fig_legend=True,
            ),
            axes=ax,
        )
    if show:
        backend.show_figure(fig)
    else:
        return fig
