from matplotlib import pyplot as plt

from pybop.plot.matplotlib import plot_trace
from pybop.plot.util import _AxisData


def create_figure(traces, **layout_options):
    figsize = (8, 6)
    if "figsize" in layout_options:
        figsize = layout_options.get("figsize")

    fig = plt.figure(figsize=figsize, dpi=100)

    for trace in traces:
        plot_trace(trace, fig)

    update_layout(fig, **layout_options)
    return fig


def update_layout(fig, axes=None, **layout_options):
    if axes is None:
        axes = [plt.gca()]
    if "title" in layout_options:
        plt.suptitle(layout_options.get("title"))
    if "xaxis_title" in layout_options:
        plt.xlabel(layout_options.get("xaxis_title"))
    if "yaxis_title" in layout_options:
        plt.ylabel(layout_options.get("yaxis_title"))
    if "grid" in layout_options:
        grid = layout_options.get("grid")
        plt.grid(**grid)
    if "xaxis_range" in layout_options:
        plt.xlim(layout_options.get("xaxis_range"))
    if "yaxis_range" in layout_options:
        plt.ylim(layout_options.get("yaxis_range"))
    if "figsize" in layout_options:
        fig.set_size_inches(layout_options.get("figsize"))

    # plt.tick_params(axis="both", labelsize=12)
    # plt.ticklabel_format(axis="both", style="sci", scilimits=(-4, 4))

    for ax in axes:
        if "axis_bg_color" in layout_options:
            ax.set_facecolor(layout_options.get("axis_bg_color"))
            ax.set_axisbelow(True)
        if (
            not ax.get_legend_handles_labels() == ([], [])
            and "fig_legend" not in layout_options
        ):
            ax.legend(layout_options.get("legend") or {})

    if "fig_legend" in layout_options:
        labels_in_fig = False
        lines_labels = []
        for ax in axes:
            if not ax.get_legend_handles_labels() == ([], []):
                lines_labels.append(ax.get_legend_handles_labels())
                labels_in_fig = True
        if labels_in_fig:
            lines, labels = [sum(lol, []) for lol in zip(*lines_labels, strict=False)]
            opts = dict(loc="best", fontsize=12)
            opts.update(layout_options.get("fig_legend") or {})
            if opts.get("horizontal"):
                opts["ncols"] = len(lines)
                del opts["horizontal"]
            fig.legend(lines, labels, **opts)

    if "tight_layout" in layout_options:
        plt.tight_layout(**layout_options.get("tight_layout"))


def make_subplots(axes: list[_AxisData], subplot_options=None):
    subplot_options = subplot_options or {}

    num_rows = max(ax.row + ax.row_span - 1 for ax in axes)
    num_cols = max(ax.col + ax.col_span - 1 for ax in axes)

    fig = plt.figure()

    for i, ax in enumerate(axes):
        idx_start = (ax.row - 1) * num_cols + ax.col
        idx_end = (ax.row + ax.row_span - 2) * num_cols + ax.col + ax.col_span - 1
        axes[i] = fig.add_subplot(num_rows, num_cols, (idx_start, idx_end))

    return fig
