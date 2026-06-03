import numpy as np

from pybop.plot.backends.base import PlotBackend
from pybop.plot.util import AxisData, wrap_text


class MatplotlibBackend(PlotBackend):
    """
    Matplotlib implementation of the PlotBackend interface.
    This backend converts backend-agnostic trace definitions into
    Matplotlib figures, axes, and artists. Plot objects are represented
    as dictionaries containing plotting arguments and metadata, allowing
    higher-level plotting code to remain independent of the underlying
    plotting library.
    """

    def __init__(self):
        # Import matplotlib only when needed
        import matplotlib as mpl
        from matplotlib import pyplot as plt

        self.mpl = mpl
        self.plt = plt

        # Backend identifier used by utility functions and text wrapping.
        self.name = "matplotlib"

        # Enable automatic colour cycling across subplots when traces do not
        # explicitly define a colour.
        self.global_colorcycle = False

        # Matplotlib's default property cycle.
        self.colorcycle = self.plt.rcParams["axes.prop_cycle"]()

        # Layout rectangle reserved for tight_layout(). This may be adjusted
        # when legends are placed outside the plotting area.
        self.rect = [0, 0, 1, 1]

    def _figsize(self, style):
        """
        Convert pixel-based width and height values from a style dictionary
        into a Matplotlib figsize (inches).
        """
        return (
            np.ceil(style.get("width", 800) / 100),
            np.ceil(style.get("height", 600) / 100),
        )

    def create_figure(
        self, title=None, xaxis_title=None, yaxis_title=None, traces=None, style=None
    ):
        """
        Create a single-axis figure and optionally populate it with traces.

        Parameters
        ----------
        title : str, optional
            Figure title.
        xaxis_title : str, optional
            X-axis label.
        yaxis_title : str, optional
            Y-axis label.
        traces : list[dict], optional
            Trace definitions to plot immediately.
        style : dict, optional
            Figure styling options.
            Currently supported options:
                - width in pixels
                - heith in pixels
                - xaxis_range: range of the X-axis
                - yaxis_range: range of the Y-axis
                - bg_color: background color of the axis

        Returns
        -------
        matplotlib.figure.Figure
            Configured figure instance.
        """
        style = style or {}
        fig = self.plt.figure(figsize=self._figsize(style), dpi=100)

        if title is not None:
            self.plt.suptitle(title)
        if xaxis_title is not None:
            self.plt.xlabel(xaxis_title)
        if yaxis_title is not None:
            self.plt.ylabel(yaxis_title)

        # Apply backend-supported figure styling options.
        if "xaxis_range" in style:
            self.plt.xlim(style.get("xaxis_range"))
        if "yaxis_range" in style:
            self.plt.ylim(style.get("yaxis_range"))
        if "bg_color" in style:
            ax = fig.gca()
            ax.set_facecolor(style.get("bg_color"))
            ax.set_axisbelow(True)

        if traces is not None:
            for trace in traces:
                self.plot_trace(trace, fig)
        return fig

    def make_subplots(
        self,
        axes: list[AxisData],
        title=None,
        xaxis_titles: list[str] | str = None,
        yaxis_titles: list[str] | str = None,
        style=None,
    ):
        """
        Create a figure containing a custom subplot layout.

        The layout is defined by a collection of AxisData objects, which
        specify subplot positions and spans within a grid.

        Parameters
        ----------
        title : str, optional
            Figure title.
        xaxis_title : str, optional
            X-axis label.
        yaxis_title : str, optional
            Y-axis label.
        traces : list[dict], optional
            Trace definitions to plot immediately.
        style : dict, optional
            Figure styling options.
            Currently supported options:
                - width in pixels
                - heith in pixels
                - bg_color: background color of the axis

        Returns
        -------
        matplotlib.figure.Figure
            Configured figure instance.
        """

        style = style or {}

        # Create figure
        fig = self.plt.figure(figsize=self._figsize(style), dpi=100)
        if title is not None:
            self.plt.suptitle(title)

        # Determine the minimum grid size required to accommodate all subplot spans.
        num_rows = max(ax.row + ax.row_span - 1 for ax in axes)
        num_cols = max(ax.col + ax.col_span - 1 for ax in axes)

        axes_dict = {}
        for ax in axes:
            # Convert row/column span information into Matplotlib subplot indices.
            idx_start = (ax.row - 1) * num_cols + ax.col
            idx_end = (ax.row + ax.row_span - 2) * num_cols + ax.col + ax.col_span - 1
            axes_dict[(ax.row, ax.col)] = fig.add_subplot(
                num_rows, num_cols, (idx_start, idx_end)
            )

        # Helper to support either a shared axis title or per-axis titles.
        def _get_axis_title(titles, i):
            if isinstance(titles, str):
                return titles
            if isinstance(titles, list) and i < len(titles):
                return titles[i]
            return None

        # Reduce wrapping width as the number of subplot rows increases.
        width = np.floor(50 / num_rows)
        for i, ax in enumerate(fig.axes):
            if title := _get_axis_title(xaxis_titles, i):
                ax.set_xlabel(wrap_text(title, width, self.name))
            if title := _get_axis_title(yaxis_titles, i):
                ax.set_ylabel(wrap_text(title, width, self.name))
            if "bg_color" in style:
                ax.set_facecolor(style.get("bg_color"))
                ax.set_axisbelow(True)

        # Use a shared colour cycle across all subplot axes.
        self.global_colorcycle = True

        return fig, axes_dict, num_rows, num_cols

    def legend(self, fig, style: dict = None):
        """
        Create an axis-level or figure-level legend.

        Supports legends positioned outside the plotting area and updates
        the layout rectangle used by tight_layout() accordingly.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure object
        style : dict, optional
            Legend styling options.
            Currently supported options:
                - loc: str
                - coords: tuple - is translated into bbox_to_anchor
                - outside: tuple(side : str, offset: float) places
                    the legend outside the plot, where the side (left,
                    right, top, bottom) determines on wich side of the plot
                    the legend is placed and the offset determines the fraction
                    of the figure height or width reserved for the legend.
                    Overrides loc and coords.
                - fig_legend: if true, one legend is created for the entire figure, otherwise the legend is created
                    for the current axis.

        """
        style = style or {}
        lines_labels = []
        if style.get("fig_legend"):
            axes = fig.axes
        else:
            axes = [fig.gca()]

        # Configure external legend placement and reserve layout space.
        if "outside" in style.keys():
            side, offset = style.get("outside")
            if side == "left":
                style["loc"] = "upper left"
                style["coords"] = (0.0, 1.0)
                self.rect = [offset, 0, 1, 1]
            elif side == "top":
                style["loc"] = "lower right"
                style["coords"] = (1.0, 1.0 - offset)
                self.rect = [0, 0, 1, 1 - offset]
            elif side == "bottom":
                style["loc"] = "lower left"
                style["coords"] = (0.0, 0.0)
                self.rect = [0, offset, 1, 1]
            else:
                style["loc"] = "upper right"
                style["coords"] = (1.0, 1.0)
                self.rect = [0.0, 0, 1 - offset, 1]

        # Collect legend entries from all relevant axes.
        labels_in_fig = False
        lines_labels = []
        opts = {}
        for ax in axes:
            # Flatten handles and labels from multiple axes into a single legend.
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                lines_labels.append((handles, labels))
                labels_in_fig = True

        if labels_in_fig:
            lines, labels = [sum(lol, []) for lol in zip(*lines_labels, strict=False)]
            if style.get("horizontal"):
                opts["ncols"] = len(lines)
            if "coords" in style.keys():
                opts["bbox_to_anchor"] = style.get("coords")
            if style.get("fig_legend"):
                opts["loc"] = style.get("loc", "upper right")
                fig.legend(lines, labels, **opts)
            else:
                opts["loc"] = style.get("loc", "best")
                axes[0].legend(lines, labels, **opts)

    def show_figure(self, fig):
        """
        Apply final layout adjustments and display the figure.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure object
        """

        if isinstance(fig, list):
            for f in fig:
                f.tight_layout(rect=self.rect)
        else:
            fig.tight_layout(rect=self.rect)
        self.plt.show()

    def plot_trace(self, traces: dict | list[dict], fig, ax=None):
        """
        Convert one or more trace definitions into Matplotlib plotting calls.

        Parameters
        ----------
        traces: dict or list[dict]
            Each trace dictionary specifies a plotting method, positional
            arguments, and keyword arguments compatible with a Matplotlib Axes
            method.
        fig : matplotlib.figure.Figure
            The figure object
        ax : matplotlib axis object, optional
            Specity an axis for plotting. Otherwise current axis is used.
        """

        traces = traces if isinstance(traces, list) else [traces]

        # Extract plotting keyword arguments while removing backend metadata.
        ax = ax or fig.gca()
        for trace in traces:
            if title := trace.get("xaxis_title"):
                ax.set_xlabel(title)
            if title := trace.get("yaxis_title"):
                ax.set_ylabel(title)

            options = {
                k: v
                for k, v in trace.items()
                if k
                not in {
                    "plot_type",
                    "positional_args",
                    "xaxis_title",
                    "yaxis_title",
                }
            }
            plot_type = trace.get("plot_type", "plot")
            args = trace.get("positional_args", ())

            # Apply the global colour cycle when plotting standard line traces.
            if self.global_colorcycle and plot_type == "plot":
                options.update(next(self.colorcycle))
            # Resolve the requested plotting method on the target axis.
            plot_func = getattr(ax, plot_type)

            obj = plot_func(*args, **options)

            # Automatically attach a colourbar for filled contour plots.
            if plot_type == "contourf":
                self.plt.colorbar(obj)

    def sample_color_scale(self, data, scale="viridis", d_min=None, d_max=None):
        """
        Map data values to RGBA colours using a Matplotlib colormap.

        Parameters
        ----------
        data: ndarray
            The data to be mapped
        scale : str
            Name of the colormap
        d_min: float, optional
            Minimum value to be mapped. Otherwise the minimum of the data is used.
        d_max: float, optional
            Maximum value to be mapped. Ohterwise maximum of the data is used.
        """
        # Normalise values into the range expected by the colormap.
        d_min = d_min or np.nanmin(data[np.isfinite(data)])
        d_max = d_max or np.nanmax(data[np.isfinite(data)])
        norm = self.mpl.colors.Normalize(vmin=d_min, vmax=d_max, clip=True)
        norm_d = norm(data, clip=True)
        if np.isscalar(norm_d):
            norm_d = [norm_d]

        # Sample colours from the requested colormap.
        cmap = self.mpl.colormaps[scale]
        return cmap(norm_d)

    def colorbar(self, fig, data, colorscale="viridis", label=None):
        """
        Add colourbar to figure

        Parameters
        ----------
        fig: matplotlib.figure.Figure
            The figure.
        data: array-like
            The data to be mapped
        scale : str
            Name of the colormap
        label: str, optional
            label to be displayed alongside colorbar
        """
        # Create a normalisation matching the supplied data range.
        f_min = np.nanmin(data[np.isfinite(data)])
        f_max = np.nanmax(data[np.isfinite(data)])
        norm = self.mpl.colors.Normalize(vmin=f_min, vmax=f_max, clip=True)

        # Create and attach a standalone colourbar.
        cmap = self.mpl.colormaps[colorscale]
        self.plt.colorbar(
            self.mpl.cm.ScalarMappable(norm=norm, cmap=cmap), ax=fig.gca(), label=label
        )

    def contour_plot(self, x, y, z, colorscale="viridis"):
        """
        Return trace definitions for a filled contour plot and contour lines.

        Parameters
        ----------
        x, y : array-like
            Coordinate values.
        z : array-like
            Surface values.
        colorscale : str, optional
            Colour scale name.

        Returns
        -------
        object
            dictionary for contour plot definition and
            dictionary for contour line definition
        """
        contour = dict(positional_args=[x, y, z], plot_type="contourf", cmap=colorscale)
        contour_lines = dict(
            positional_args=[x, y, z],
            colors=("k"),
            linestyles="solid",
            linewidths=0.2,
            plot_type="contour",
        )
        return [contour, contour_lines]

    def fill(self, x, y, color=None, label=None):
        """
        Return a trace definition for a filled polygon.

        Parameters
        ----------
        x, y : array-like
            Coordinates defining the filled area.
        color : str, optional
            Fill colour.
        label : str, optional
            Ignored by the matplotlib implementation.
        """
        return dict(positional_args=(x, y), plot_type="fill", color=color)

    def fill_between(self, x, y_upper, y_lower, color):
        """
        Return a trace definition for a filled region between two curves.

        Parameters
        ----------
        x : array-like
            X-axis values.
        y_upper : array-like
            Upper boundary values.
        y_lower : array-like
            Lower boundary values.
        color : str
            Fill colour.
        """
        return {
            "positional_args": (x, y_upper, y_lower),
            "plot_type": "fill_between",
            "color": color,
        }

    def histogram_plot(self, x, name, style: dict = None):
        """
        Return a trace definition for a histogram.

        Parameters
        ----------
        x : array-like
            Data to bin.
        name : str
            Histogram label.
        style : dict, optional
            Currently only 'alpha' supported for opacity.
            All other style arguments ignored.
        """
        style = style or {}

        return {
            "positional_args": [x],
            "label": name,
            "plot_type": "hist",
            "alpha": style.get("alpha"),
        }

    def line(self, x=None, y=None, label=None, style=None):
        """
        Return a trace definition for a line plot.

        Parameters
        ----------
        x, y : array-like, optional
            Coordinates of the line.
            If both x and y are provided, the shorter sequence determines the
            plotted length.
        label : str, optional
            Trace label.
        style : dict, optional
            Line styling options.

        Returns
        -------
        object
            dictionary with positional argumetns, label and style arguments
        """
        style = style or {}
        if y is None:
            raise ValueError("y must be provided")

        args = [y]
        if x is not None:
            size = min(len(x), len(y))
            args = [x[:size], y[:size]]

        return {
            "positional_args": args,
            "label": label,
            **style,
        }

    def scatter(self, x, y, colors=None, labels=None, colorscale="Greys"):
        """
        Return a trace definition for a scatter plot.

        Parameters
        ----------
        x, y : array-like
            Point coordinates.
        colors : array-like
            Values or colours associated with each point.
        labels : array-like, optional
            Point labels.
            Point labels are ignored by matplotlib implementation.
            Argument retained for consistency with plotly.
        colorscale : str, optional
            Colour scale name.
        """
        scatter = {
            "positional_args": [x, y],
            "plot_type": "scatter",
            "cmap": colorscale,
        }
        if colors is not None:
            scatter["c"] = colors
        return scatter

    def show_table(self, header, values, title):
        """
        Display tabular data in a standalone Matplotlib figure.

        Array-valued entries are converted to comma-separated strings before
        rendering.

        Parameters
        ----------
        header : list
            Column headers.
        values : list
            Table contents.
        title : str
            Table title.
        """
        for i, val in enumerate(values):
            values[i] = [val[0], ", ".join(val[1].astype(str))]

        fig, ax = self.plt.subplots(figsize=(6, 2), dpi=100)

        # Remove axis decorations so only the table is displayed.
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
        self.plt.show()

    def vline(self, fig, x, style=None):
        """
        Add a vertical reference line to the current axis.

        Parameters
        ----------
        fig: matplotlib.figure.Figure
            The figure.
        x: float
            The position of the vertical line on the axis
        style: dict, optional
            matplotlib arguments for axvline method
        """
        fig.gca()
        style = style or {}
        self.plt.axvline(x, **style)
