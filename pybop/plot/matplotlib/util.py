import warnings

import matplotlib.pyplot as plt


def update_and_show(fig, show=True, **layout_kwargs):
    if len(layout_kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(layout_kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )

    if show:
        plt.show()

    return fig


DEFAULT_PLOT_OPTIONS = {
    "contour": {
        "plot_options": dict(title="Cost Landscape"),
        "trace_options_contour": dict(extend="both", cmap="viridis"),
        "trace_options_initial": dict(
            marker="X",
            markersize=14,
            markerfacecolor="w",
            markeredgecolor="k",
            label="Initial values",
            linestyle="None",
        ),
        "trace_options_optim": dict(
            marker="P",
            markersize=14,
            markerfacecolor="k",
            markeredgecolor="w",
            label="Final values",
            linestyle="None",
        ),
    },
    "nyquist": {
        "plot_options": dict(
            xaxis_title=r"$Z_{re} / \Omega$", yaxis_title=r"$-Z_{im} / \Omega$"
        ),
        "trace_options_model": dict(
            label="Model", color="#00CC96", linewidth=2, marker=".", markersize=8
        ),
        "trace_options_reference": dict(
            label="Reference",
            linestyle="none",
            marker="o",
            fillstyle="none",
            markersize=8,
            markeredgecolor="#636EFA",
        ),
    },
    "parameters": dict(figsize=(18, 8), title="Parameter Convergence"),
    "problem": {
        "default_trace_options": dict(label="Model", marker=None, linestyle="-"),
        "design_cost_options": dict(label="Optimised"),
        "meta_problem_options": dict(marker=".", linestyle="none"),
        "reference_options": dict(label="Reference", marker=".", linestyle="none"),
        "fill_options": dict(color=[(1.0, 0.898, 0.800, 0.8)]),
    },
    "posterior": {
        "plot_options": {
            "figsize": (15, 8),
            "grid": dict(axis="y", zorder=-1, color="w"),
            "axis_bg_color": (
                0.6784313725490196,
                0.8470588235294118,
                0.9019607843137255,
                0.3,
            ),
        },
        "trace_options": dict(alpha=0.75),
        "trace_options_vline": dict(linewidth=3, linestyle="--", color="k"),
    },
    "trace": {
        "plot_options": {
            "figsize": (15, 8),
            "grid": dict(axis="y", zorder=-10, color="w"),
            "axis_bg_color": (
                0.6784313725490196,
                0.8470588235294118,
                0.9019607843137255,
                0.3,
            ),
        },
    },
}
