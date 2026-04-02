import warnings
from typing import TYPE_CHECKING

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from pybop._result import Result

from pybop.plot.voronoi import voronoi_data


def surface(
    result: "Result",
    bounds=None,
    normalise=True,
    title="Voronoi Cost Landscape",
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
    """

    if len(layout_kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(layout_kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )

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

    _, _, f, regions, relative_sizes = voronoi_data(
        xlim, ylim, x_optim, y_optim, f, normalise
    )

    # Construct figure
    plt.figure(figsize=(7, 6), dpi=100)

    # normalise cost
    f_min = np.nanmin(f[np.isfinite(f)])
    f_max = np.nanmax(f[np.isfinite(f)])
    norm = mpl.colors.Normalize(vmin=f_min, vmax=f_max, clip=True)
    norm_f = norm(f, clip=True)

    # get colours
    cmap = mpl.colormaps["viridis"]
    colors = cmap(norm_f)

    # Add Voronoi edges and fill Voronoi regions
    for j, (region, size) in enumerate(zip(regions, relative_sizes, strict=False)):
        x_region = region[:, 0].tolist() + [region[0, 0]]
        y_region = region[:, 1].tolist() + [region[0, 1]]

        plt.fill(x_region, y_region, color=colors[j])
        plt.plot(x_region, y_region, color="w", linewidth=0.5 + size * 0.1)

    plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=plt.gca())

    # Add original points
    plt.scatter(
        x_optim,
        y_optim,
        c=[i / len(x_optim) for i in range(len(x_optim))],
        cmap="Grays",
        zorder=2.5,
    )

    # Plot the initial guess
    if len(result.x_model) > 0:
        x0 = result.x_model[0]
        plt.plot(
            [x0[0]],
            [x0[1]],
            "X",
            markersize=14,
            markerfacecolor="w",
            markeredgecolor="k",
            label="Initial values",
            linestyle="None",
            zorder=2.6,
        )

    # Plot optimised value
    if result.x is not None:
        x_best = result.x
        plt.plot(
            [x_best[0]],
            [x_best[1]],
            "P",
            markersize=14,
            markerfacecolor="k",
            markeredgecolor="w",
            label="Final values",
            linestyle="None",
            zorder=2.6,
        )

    # Layout
    names = result.problem.parameters.names
    plt.xlabel(names[0], labelpad=15)
    plt.ticklabel_format(axis="both", **dict(style="sci", scilimits=(-4, 4)))
    plt.ylabel(names[1], labelpad=15)
    plt.title(title, pad=40)
    plt.legend(ncols=2, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    plt.xlim(xlim[0], xlim[1])
    plt.ylim(ylim[0], ylim[1])
    plt.tight_layout()

    if show:
        plt.show()
