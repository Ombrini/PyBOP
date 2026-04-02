from typing import TYPE_CHECKING

import numpy as np
from scipy.spatial import cKDTree

if TYPE_CHECKING:
    from pybop._result import Result
from pybop.plot import voronoi_data
from pybop.plot.plotly.plotly_manager import PlotlyManager


def assign_nearest_value(x, y, f, xi, yi):
    """
    Computes an array of values given by the score of the nearest point.

    Parameters
    ----------
    x : array-like
        The x coordinates of points with known scores.
    y : array-like
        The y coordinates of points with known scores.
    f : array-like
        The score function at the given x and y coordinates.
    xi : array-like
        The x coordinates of grid points.
    yi : array-like
        The y coordinates of grid points.

    Returns
    -------
        A numpy array containing the scores corresponding to the grid points.
    """
    # Create a KD-tree for efficient nearest neighbor search
    tree = cKDTree(np.column_stack((x, y)))

    # Find the nearest point for each grid point
    _, indices = tree.query(np.column_stack((xi.ravel(), yi.ravel())))
    zi = f[indices].reshape(xi.shape)

    return zi


def surface(
    result: "Result",
    bounds=None,
    normalise=True,
    resolution=250,
    show=True,
    **layout_kwargs,
):
    """
    Plot a 2D representation of the Voronoi diagram with color-coded regions.

    Parameters:
    -----------
    result : pybop.Result
        Optimisation result containing the history of parameter values and associated cost.
    bounds : numpy.ndarray, optional
        A 2x2 array specifying the [min, max] bounds for each parameter. If None, uses
        `cost.parameters.get_bounds_for_plotly`.
    normalise : bool, optional
        If True, the voronoi regions are computed using the Euclidean distance between
        points normalised with respect to the bounds (default: True).
    resolution : int, optional
        Resolution of the plot. Default is 500.
    show : bool, optional
        If True, the figure is shown upon creation (default: True).
    **layout_kwargs : optional
        Valid Plotly layout keys and their values,
        e.g. `xaxis_title="Time [s]"` or
        `xaxis={"title": "Time [s]", font={"size":14}}`
    """
    points = result.x_model
    parameters = result.problem.parameters

    if points[0].shape[0] != 2:
        raise ValueError("This plot method requires two parameters.")

    x_optim, y_optim = map(list, zip(*points, strict=False))
    f = result.cost

    # Translate bounds, taking only the first two elements
    xlim, ylim = (
        bounds if bounds is not None else [param.bounds for param in parameters]
    )[:2]

    x, y, f, regions, relative_sizes = voronoi_data(
        xlim, ylim, x_optim, y_optim, f, normalise
    )

    # Create a grid for plot
    xi = np.linspace(xlim[0], xlim[1], resolution)
    yi = np.linspace(ylim[0], ylim[1], resolution)
    xi, yi = np.meshgrid(xi, yi)

    if normalise:
        # Create a normalised grid
        norm_xi = np.linspace(0, 1, resolution)
        norm_xi, norm_yi = np.meshgrid(norm_xi, norm_xi)

        # Assign a value to each point in the grid
        zi = assign_nearest_value(x, y, f, norm_xi, norm_yi)
    else:
        # Assign a value to each point in the grid
        zi = assign_nearest_value(x, y, f, xi, yi)

    # Calculate the size of each Voronoi region
    region_sizes = np.array([len(region) for region in regions])
    relative_sizes = (region_sizes - region_sizes.min()) / (
        region_sizes.max() - region_sizes.min()
    )

    # Construct figure
    go = PlotlyManager().go
    fig = go.Figure()

    # Heatmap
    fig.add_trace(
        go.Heatmap(
            x=xi[0],
            y=yi[:, 0],
            z=zi,
            colorscale="Viridis",
            zsmooth="best",
        )
    )

    # Add Voronoi edges
    for region, size in zip(regions, relative_sizes, strict=False):
        x_region = region[:, 0].tolist() + [region[0, 0]]
        y_region = region[:, 1].tolist() + [region[0, 1]]

        fig.add_trace(
            go.Scatter(
                x=x_region,
                y=y_region,
                mode="lines",
                line=dict(color="white", width=0.5 + size * 0.1),
                showlegend=False,
            )
        )

    # Add original points
    fig.add_trace(
        go.Scatter(
            x=x_optim,
            y=y_optim,
            mode="markers",
            marker=dict(
                color=[i / len(x_optim) for i in range(len(x_optim))],
                colorscale="Greys",
                size=8,
                showscale=False,
            ),
            text=[f"f={val:.2f}" for val in f],
            hoverinfo="text",
            showlegend=False,
        )
    )

    # Plot the initial guess
    if len(result.x_model) > 0:
        x0 = result.x_model[0]
        fig.add_trace(
            go.Scatter(
                x=[x0[0]],
                y=[x0[1]],
                mode="markers",
                marker_symbol="x",
                marker=dict(
                    color="white",
                    line_color="black",
                    line_width=1,
                    size=14,
                    showscale=False,
                ),
                name="Initial values",
            )
        )

        # Plot optimised value
        if result.x is not None:
            x_best = result.x
            fig.add_trace(
                go.Scatter(
                    x=[x_best[0]],
                    y=[x_best[1]],
                    mode="markers",
                    marker_symbol="cross",
                    marker=dict(
                        color="black",
                        line_color="white",
                        line_width=1,
                        size=14,
                        showscale=False,
                    ),
                    name="Final values",
                )
            )

    names = parameters.names
    fig.update_layout(
        title="Voronoi Cost Landscape",
        title_x=0.5,
        title_y=0.905,
        xaxis_title=names[0],
        yaxis_title=names[1],
        width=600,
        height=600,
        xaxis=dict(range=xlim, showexponent="last", exponentformat="e"),
        yaxis=dict(range=ylim, showexponent="last", exponentformat="e"),
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
    )
    fig.update_layout(**layout_kwargs)
    if show:
        fig.show()
