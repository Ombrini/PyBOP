import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np

from pybop.plot.util import get_backend
from pybop.problems.problem import Problem

if TYPE_CHECKING:
    from pybop._result import Result


def contour(
    call_object: "Problem | Result",
    gradient: bool = False,
    bounds: np.ndarray | None = None,
    transformed: bool = False,
    steps: int = 10,
    title="Cost Landscape",
    show: bool = True,
    backend: str = None,
):
    """
    Plot a 2D visualisation of a cost landscape using Plotly.

    This function generates a contour plot representing the cost landscape for a provided
    callable cost function over a grid of parameter values within the specified bounds.

    Parameters
    ----------
    call_object : pybop.Problem | pybop.Result
        Either:
        - the cost function to be evaluated. Must accept a list of parameter values and return a cost value.
        - an optimiser result which provides a specific optimisation trace overlaid on the cost landscape.
    title: str, optional
        The title of the figure (default: "Cost Landscape")
    gradient : bool, optional
        If True, the gradient is shown (default: False).
    bounds : numpy.ndarray | list[list[float]], optional
        A 2x2 array specifying the [min, max] bounds for each parameter. If None, uses
        `parameters.get_bounds_for_plotly`.
    transformed : bool, optional
        Uses the transformed parameter values (as seen by the optimiser) for plotting.
    steps : int, optional
        The number of grid points to divide the parameter space into along each dimension (default: 10).
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    backend: str, optional
        The plotting backend to be used.

    Returns
    -------
    fig : plotly.graph_objs.Figure or matplotlib.figure.Figure
        The figure object containing the cost landscape plot.

    Raises
    ------
    ValueError
        If the cost function does not return a valid cost when called with a parameter list.
    """
    backend_module = get_backend(backend)

    plot_optim = False
    problem = call_object

    # Assign input as a cost or optimisation result
    if not isinstance(call_object, Callable):
        plot_optim = True
        result = call_object
        problem = result.problem

    parameters = problem.parameters
    names = parameters.names
    additional_values = []

    if len(parameters) < 2:
        raise ValueError("This cost function takes fewer than 2 parameters.")

    if len(parameters) > 2:
        warnings.warn(
            "This cost function requires more than 2 parameters. "
            "Plotting in 2d with fixed values for the additional parameters.",
            UserWarning,
            stacklevel=2,
        )
        for (
            i,
            (name, param),
        ) in enumerate(parameters.items()):
            if i > 1:
                # TODO: Update from the initial to the intended value
                additional_values.append(param.get_initial_value())
                print(f"Fixed {name}:", param.get_initial_value())

    # Set up parameter bounds
    if bounds is None:
        bounds = parameters.get_bounds_for_plotly()
    else:
        bounds = np.asarray(bounds)

    # Generate grid
    x = np.linspace(bounds[0, 0], bounds[0, 1], steps)
    y = np.linspace(bounds[1, 0], bounds[1, 1], steps)

    # Initialize cost matrix
    costs = np.zeros((len(y), len(x)))

    if gradient:
        grad_parameter_costs = []

        # Create an array to hold the gradient with respect to each parameter
        grads = [np.zeros((len(y), len(x))) for _ in range(len(parameters))]

    # Populate cost matrix
    for i, xi in enumerate(x):
        for j, yj in enumerate(y):
            if gradient:
                out = problem.evaluate(
                    np.asarray([xi, yj] + additional_values),
                    calculate_sensitivities=True,
                ).get_values()
                costs[j, i], sensitivities = out[0][0], out[1]
                for k, key in enumerate(problem.parameters.names):
                    grads[k][j, i] = sensitivities[key].item()
            else:
                costs[j, i] = problem.evaluate(
                    np.asarray([xi, yj] + additional_values),
                ).get_values()[0]

    # Append the arrays to the grad_parameter_costs list
    if gradient:
        grad_parameter_costs.extend(grads)

    # Apply any transformation if requested
    def transform_array_of_values(list_of_values, parameter):
        """Apply transformation if requested."""
        if transformed:
            return np.asarray(
                [parameter.transformation.to_search(value) for value in list_of_values]
            ).flatten()
        return list_of_values

    x = transform_array_of_values(x, parameters[names[0]])
    y = transform_array_of_values(y, parameters[names[1]])
    bounds[0] = transform_array_of_values(bounds[0], parameters[names[0]])
    bounds[1] = transform_array_of_values(bounds[1], parameters[names[1]])

    figure_style = {
        "width": 600,
        "height": 600,
        "xaxis_range": bounds[0],
        "yaxis_range": bounds[1],
    }

    fig = backend_module.create_figure(
        title=title,
        xaxis_title="Transformed " + names[0] if transformed else names[0],
        yaxis_title="Transformed " + names[1] if transformed else names[1],
        style=figure_style,
    )

    # Create contour plot and update the layout
    backend_module.plot_trace(backend_module.contour_plot(x=x, y=y, z=costs), fig)

    if plot_optim:
        # Plot the optimisation trace
        optim_trace = np.asarray([item[:2] for item in result.x_model])
        optim_trace = optim_trace.reshape(-1, 2)
        backend_module.plot_trace(
            backend_module.scatter(
                transform_array_of_values(optim_trace[:, 0], parameters[names[0]]),
                transform_array_of_values(optim_trace[:, 1], parameters[names[1]]),
                [i / optim_trace.shape[0] for i in range(optim_trace.shape[0])],
            ),
            fig,
        )

        # Plot the initial guess
        if len(result.x_model) > 0:
            x0 = result.x_model[0]
            backend_module.plot_trace(
                backend_module.line(
                    x=transform_array_of_values([x0[0]], parameters[names[0]]),
                    y=transform_array_of_values([x0[1]], parameters[names[1]]),
                    label="Initial values",
                    style=dict(
                        marker="X",
                        markersize=14,
                        markerfacecolor="white",
                        markeredgecolor="black",
                        linestyle="None",
                        zorder=2.6,
                    ),
                ),
                fig,
            )

        # Plot optimised value
        if result.x is not None:
            x_best = result.x
            backend_module.plot_trace(
                backend_module.line(
                    x=transform_array_of_values([x_best[0]], parameters[names[0]]),
                    y=transform_array_of_values([x_best[1]], parameters[names[1]]),
                    style=dict(
                        marker="P",
                        markersize=14,
                        markerfacecolor="black",
                        markeredgecolor="white",
                        linestyle="None",
                        zorder=2.6,
                    ),
                    label="Final values",
                ),
                fig,
            )

    backend_module.legend(
        fig,
        style={
            "horizontal": True,
            "loc": "lower right",
            "coords": (1, 1),
        },
    )
    # display the figure
    if show:
        backend_module.show_figure(fig)

    if gradient:
        grad_figs = []
        for i, grad_costs in enumerate(grad_parameter_costs):
            # Create fig
            grad_fig = backend_module.create_figure(
                title=f"Gradient for Parameter: {i + 1}",
                xaxis_title="Transformed " + names[0] if transformed else names[0],
                yaxis_title="Transformed " + names[1] if transformed else names[1],
                style=figure_style,
            )

            backend_module.plot_trace(
                backend_module.contour_plot(x=x, y=y, z=grad_costs), grad_fig
            )

            if show:
                backend_module.show_figure(grad_fig)

            # append grad_fig to list
            grad_figs.append(grad_fig)

        return fig, grad_figs

    return fig
