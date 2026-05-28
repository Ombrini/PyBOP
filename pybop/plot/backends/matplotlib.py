import warnings
from copy import deepcopy

import matplotlib as mpl
import numpy as np
from matplotlib import pyplot as plt
from pybop.plot.util import _AxisData
from pybop.plot.backends.base import PlotBackend

class MatplotlibBackend(PlotBackend):
    def __init__(self):
        self.name = 'matplotlib'

    def create_figure(self, title = None, xaxis_title = None, yaxis_title = None, traces = None, style = None):
        style = style or {}
        figsize = (np.ceil(style.get("width", 800)/100), np.ceil(style.get("height", 600)/100))
        
        fig = plt.figure(figsize=figsize, dpi=100)

        # Set titles
        if title is not None:
            plt.suptitle(title)
        if xaxis_title is not None:
            plt.xlabel(xaxis_title)
        if yaxis_title is not None:
            plt.ylabel(yaxis_title)

        # Apply style
        if "xaxis_range" in style:
            plt.xlim(style.get("xaxis_range"))
        if "yaxis_range" in style:
            plt.ylim(style.get("yaxis_range"))
        if "bg_color" in style:
            ax = fig.gca()
            ax.set_facecolor(style.get("bg_color"))
            ax.set_axisbelow(True)


        if traces is not None:
            for trace in traces:
                self.plot_trace(trace, fig)
        return fig
    def make_subplots(self, axes: list[_AxisData], title=None, axis_titles_x: list[str] | str = None, axis_titles_y: list[str] | str = None, style=None):
        style = style or {}

        num_rows = max(ax.row + ax.row_span - 1 for ax in axes)
        num_cols = max(ax.col + ax.col_span - 1 for ax in axes)

        figsize = (np.ceil(style.get("width", 800)/100), np.ceil(style.get("height", 600)/100))

        fig = plt.figure(figsize=figsize, dpi=100)
        axes_dict = {}

        for ax in axes:
            print(ax)
            idx_start = (ax.row - 1) * num_cols + ax.col
            idx_end = (ax.row + ax.row_span - 2) * num_cols + ax.col + ax.col_span - 1
            axes_dict[(ax.row, ax.col)] = fig.add_subplot(num_rows, num_cols, (idx_start, idx_end))


        # Set title
        if title is not None:
            plt.suptitle(title)

        for i, ax in enumerate(fig.axes):
            if isinstance(axis_titles_x, str):
                ax.set_xlabel(axis_titles_x)
            elif isinstance(axis_titles_x, list) and i < len(axis_titles_x):
                ax.set_xlabel(axis_titles_x[i])
            if isinstance(axis_titles_y, str):
                ax.set_ylabel(axis_titles_y)
            elif isinstance(axis_titles_y, list) and i < len(axis_titles_y):
                ax.set_ylabel(axis_titles_y[i])
            if "bg_color" in style:
                ax.set_facecolor(style.get("bg_color"))
                ax.set_axisbelow(True)

        return fig, axes_dict, num_rows, num_cols

    def legend(self, fig, style: dict=None):
        style= style or {}
        lines_labels = []
        if style.get('fig_legend'):
            axes = fig.axes
        else:
            axes = [fig.gca()]
        labels_in_fig = False
        lines_labels = []
        opts ={}
        for ax in axes:
            if not ax.get_legend_handles_labels() == ([], []):
                lines_labels.append(ax.get_legend_handles_labels())
                labels_in_fig = True
        if labels_in_fig:
            lines, labels = [sum(lol, []) for lol in zip(*lines_labels, strict=False)]
            if style.get("horizontal"):
                opts["ncols"] = len(lines)
            if "coords" in style.keys():
                opts["bbox_to_anchor"] = style.get("coords")
            if style.get('fig_legend'):
                opts["loc"] = style.get("loc", "upper right")
                fig.legend(lines, labels, **opts)
            else:
                opts["loc"] = style.get("loc", "best")
            axes[0].legend(lines, labels, **opts)

    def show_figure(self, fig):
        fig.tight_layout()
        plt.show()


    def plot_trace(self, traces: dict | list[dict], fig, ax=None, color_cycle=None):
        if not isinstance(traces, list):
            traces = [traces]
        for trace in traces:
            # retrieve axis, plot_type and positional arguments
            plot_type = trace.get("plot_type") or "plot"
            positional_args = trace.get("positional_args") or None
            ax = ax or fig.gca()

            # axis titles
            if "xaxis_title" in trace.keys():
                ax.set_xlabel(trace["xaxis_title"])
            if "yaxis_title" in trace.keys():
                ax.set_ylabel(trace["yaxis_title"])

            # retrieve remaining arguments
            trace_options = deepcopy(trace)
            for key in ["plot_type", "positional_args", "xaxis_title", "yaxis_title"]:
                if key in trace_options.keys():
                    del trace_options[key]

            # update color
            if color_cycle is not None and plot_type == "plot":
                trace_options.update(**next(color_cycle))

            # get plotting function
            try:
                plot_function = getattr(ax, plot_type)
            except ValueError:
                print("Plot type not recognised")

            obj = plot_function(*positional_args, **trace_options)
            if plot_type == "contourf":
                plt.colorbar(obj)

    def sample_color_scale(self, data, scale="viridis", d_min=None, d_max=None):
        # normalise and clip data
        d_min = d_min or np.nanmin(data[np.isfinite(data)])
        d_max = d_max or np.nanmax(data[np.isfinite(data)])
        norm = mpl.colors.Normalize(vmin=d_min, vmax=d_max, clip=True)
        norm_d = norm(data, clip=True)
        if np.isscalar(norm_d):
            norm_d = [norm_d]

        # get colours
        cmap = mpl.colormaps[scale]
        return cmap(norm_d)
    
    def colorbar(self, fig, data, colorscale="viridis", label=None):
        # normalise cost
        f_min = np.nanmin(data[np.isfinite(data)])
        f_max = np.nanmax(data[np.isfinite(data)])
        norm = mpl.colors.Normalize(vmin=f_min, vmax=f_max, clip=True)

        # get colours
        cmap = mpl.colormaps[colorscale]

        plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=fig.gca(), label=label)

    def contour_plot(self, x, y, z, colorscale="viridis"):
        contour = dict(positional_args=[x, y, z], plot_type="contourf", cmap=colorscale)
        contour_lines = dict(
            positional_args=[x, y, z],
            colors=("k"),
            linestyles="solid",
            linewidths=0.2,
            plot_type="contour",
        )
        return [contour, contour_lines]
    
    def fill_plot(self, x, y, color=None, label=None):
        return dict(positional_args=(x, y), plot_type="fill", color=color)
    

    def fill_between_plot(self, x, y_upper, y_lower, color):
        trace = dict(positional_args=(x, y_upper, y_lower), plot_type="fill_between", color=color)
        return trace

    def histogram_plot(self, x, name, style: dict = None):
        trace = dict(positional_args=[x], label=name, plot_type="hist")
        trace.update({"alpha" : style.get("alpha")})
        return trace

    def line_plot(self, x=None, y=None, label=None, style=None):
        style = style or {}
        if x is not None and y is not None:
            size = min(len(x), len(y))
            trace = dict(positional_args=[x[:size], y[:size]], label=label)
        elif y is not None:
            trace = dict(positional_args=[y], label=label)

        trace.update(style)
        return trace

    def scatter_plot(self, x, y, colors=None, labels=None, colorscale="Greys"):
        scatter = dict(positional_args=[x, y], plot_type="scatter", cmap=colorscale)
        if colors is not None:
            scatter["c"] = colors
        return scatter

    def show_table(self, header, values, title):
        """
        Display data in a table.
        """
        for i, val in enumerate(values):
            values[i] = [val[0], ", ".join(val[1].astype(str))]

        fig, ax = plt.subplots(figsize=(6, 2), dpi=100)

        # hide axes
        ax.axis("off")
        ax.axis("tight")
        ax.table(
            cellText=values,
            colLabels=header,
            loc="center",
            cellLoc="center",
            colColours=["lightsteelblue", "lightsteelblue"],
        )
        ax.set_title(title)
        fig.tight_layout()
        plt.show()

    def add_vline(self, fig, x, style=None):
        fig.gca()
        style=style or {}
        plt.axvline(x, **style)





