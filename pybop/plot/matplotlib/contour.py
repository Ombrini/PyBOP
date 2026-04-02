import warnings
from collections.abc import Callable
from typing import TYPE_CHECKING

import numpy as np
from matplotlib import pyplot as plt

from pybop.problems.problem import Problem

if TYPE_CHECKING:
    from pybop._result import Result


def contour(
    call_object: "Problem | Result",
    gradient: bool = False,
    bounds: np.ndarray | None = None,
    transformed: bool = False,
    steps: int = 10,
    show: bool = True,
    title: str = "Cost Landscape",
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
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time [s]"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`

    Returns
    -------
    plotly.graph_objs.Figure
        The Plotly figure object containing the cost landscape plot.

    Raises
    ------
    ValueError
        If the cost function does not return a valid cost when called with a parameter list.
    """
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

    # define levels
    exponent = np.floor(np.log10(np.abs(np.max(costs))))
    levels = np.linspace(
        np.floor(np.min(costs) / (10**exponent)) * (10**exponent),
        np.ceil(np.max(costs) / (10**exponent)) * (10**exponent),
        2 * steps - 1,
    )

    # Create contour plot and update the layout
    fig = plt.figure(figsize=(6, 6), dpi=100)
    plt.contourf(x, y, costs, levels=levels, extend="both", cmap="viridis")
    plt.colorbar()
    plt.contour(
        x, y, costs, levels=levels, colors=("k",), linestyles="solid", linewidths=0.1
    )

    # Layout
    plt.xlabel("Transformed " + names[0] if transformed else names[0], labelpad=15)
    plt.ticklabel_format(axis="both", **dict(style="sci", scilimits=(-4, 4)))
    plt.ylabel("Transformed " + names[1] if transformed else names[1], labelpad=15)
    plt.title(title, pad=40)
    plt.xlim(bounds[0])
    plt.ylim(bounds[1])

    if plot_optim:
        # Plot the optimisation trace
        optim_trace = np.asarray([item[:2] for item in result.x_model])
        optim_trace = optim_trace.reshape(-1, 2)

        plt.scatter(
            transform_array_of_values(optim_trace[:, 0], parameters[names[0]]),
            transform_array_of_values(optim_trace[:, 1], parameters[names[1]]),
            c=[i / len(optim_trace) for i in range(len(optim_trace))],
            cmap="Grays",
            zorder=1,
        )

        # Plot the initial guess
        if len(result.x_model) > 0:
            x0 = result.x_model[0]
            plt.plot(
                transform_array_of_values([x0[0]], parameters[names[0]]),
                transform_array_of_values([x0[1]], parameters[names[1]]),
                "X",
                markersize=14,
                markerfacecolor="w",
                markeredgecolor="k",
                label="Initial values",
                linestyle="None",
            )

        # Plot optimised value
        if result.x is not None:
            x_best = result.x
            plt.plot(
                transform_array_of_values([x_best[0]], parameters[names[0]]),
                transform_array_of_values([x_best[1]], parameters[names[1]]),
                "P",
                markersize=14,
                markerfacecolor="k",
                markeredgecolor="w",
                label="Final values",
                linestyle="None",
            )

        plt.legend(ncols=2, loc="lower center", bbox_to_anchor=(0.5, 1.0))

    plt.tight_layout()

    if show:
        plt.show()

    # if gradient:
    #     grad_figs = []
    #     for i, grad_costs in enumerate(grad_parameter_costs):
    #         # Update title for gradient plots
    #         updated_layout_options = layout_options.copy()
    #         updated_layout_options["title"] = f"Gradient for Parameter: {i + 1}"

    #         # Create contour plot with updated layout options
    #         grad_layout = go.Layout(updated_layout_options)

    #         # Create fig
    #         grad_fig = go.Figure(
    #             data=[go.Contour(x=x, y=y, z=grad_costs)], layout=grad_layout
    #         )
    #         grad_fig.update_layout(**layout_kwargs)

    #         if show:
    #             grad_fig.show()

    #         # append grad_fig to list
    #         grad_figs.append(grad_fig)

    #     return fig, grad_figs

    return fig
