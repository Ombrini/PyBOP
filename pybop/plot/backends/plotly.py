import numpy as np

from pybop.plot.backends.base import PlotBackend
from pybop.plot.backends.plotly_manager import PlotlyManager
from pybop.plot.util import AxisData, wrap_text

# Mapping from Matplotlib line styles to Plotly dash styles.
LINESTYLE_MAP = {
    "solid": "solid",
    "dashed": "dash",
    "dotted": "dot",
    "dashdot": "dashdot",
}

# Mapping from Matplotlib-style marker definitions to their Plotly
# equivalents.
MARKER_MAP = {"o": "circle", "P": "cross", "X": "x", ".": None}

# Translation between Matplotlib legend anchor keywords and Plotly
# anchor names.
ANCHOR_MAP = {
    "lower": "bottom",
    "upper": "top",
    "left": "left",
    "center": "center",
    "right": "right",
}


class PlotlyBackend(PlotBackend):
    """
    Plotly implementation of the PlotBackend interface.

    This backend converts backend-agnostic plot definitions into Plotly
    figures and traces, providing interactive visualisations while
    maintaining a common plotting API.
    """

    def __init__(self):
        """
        Initialise the Plotly backend and associated Plotly manager.
        """
        self.name = "plotly"
        self.plotly_manager = PlotlyManager()

    def _figure_layout(self, style, figure_title):
        axis_layout = dict(
            title=dict(font={"size": 14}),
            showexponent="last",
            exponentformat="e",
            tickfont=dict(size=12),
        )
        return {
            "title": figure_title,
            "width": style.get("width"),
            "height": style.get("height"),
            "xaxis": axis_layout,
            "yaxis": axis_layout,
            "plot_bgcolor": style.get("bg_color"),
        }

    def create_figure(
        self,
        title: str = None,
        xaxis_title: str = None,
        yaxis_title: str = None,
        traces=None,
        style: dict = None,
    ):
        """
        Create a Plotly figure.

        Parameters
        ----------
        title : str, optional
            Figure title.
        xaxis_title : str, optional
            X-axis label.
        yaxis_title : str, optional
            Y-axis label.
        traces : list, optional
            Plotly traces to add to the figure.
        style : dict, optional
            Currently supported options:
                - width in pixels
                - heith in pixels
                - xaxis_range: range of the X-axis
                - yaxis_range: range of the Y-axis
                - bg_color: background color of the axis

        Returns
        -------
        plotly.graph_objects.Figure
            Configured Plotly figure.
        """
        style = style or {}
        layout_opts = self._figure_layout(style, title)
        layout_opts.update(
            {
                "xaxis_title": xaxis_title,
                "yaxis_title": yaxis_title,
                "xaxis_range": style.get("xaxis_range"),
                "yaxis_range": style.get("yaxis_range"),
                "barmode": "overlay",
            }
        )
        layout = self.plotly_manager.go.Layout(layout_opts)

        fig = self.plotly_manager.go.Figure(data=traces, layout=layout)
        return fig

    def _check_empty(self, specs, row, col):
        """
        Validate that a subplot grid location is available.

        Parameters
        ----------
        specs : list[list]
            Plotly subplot specification grid.
        row : int
            Row index (1-based).
        col : int
            Column index (1-based).

        Raises
        ------
        ValueError
            If the requested subplot location overlaps an existing subplot.
        """
        if specs[row - 1][col - 1] is None or len(specs[row - 1][col - 1]) > 0:
            raise ValueError("Overlapping axes are not supported")

    def make_subplots(
        self,
        axes: list[AxisData],
        title=None,
        xaxis_titles: list[str] | str = None,
        yaxis_titles: list[str] | str = None,
        style=None,
    ):
        """
        Create a figure containing multiple subplots.

        Parameters
        ----------
        axes : list[AxisData]
            Definitions describing subplot positions and spans.
        title : str, optional
            Figure title.
        xaxis_titles : str or list[str], optional
            X-axis titles.
        yaxis_titles : str or list[str], optional
            Y-axis titles.
        style : dict, optional
            Figure styling options.

        Returns
        -------
        tuple
            (
                figure,
                axes dictionary,
                number of rows,
                number of columns
            )
        """
        style = style or {}
        axes_dict = {}

        # Determine the minimum grid size required to accommodate all subplot spans.
        num_rows = max(ax.row + ax.row_span - 1 for ax in axes)
        num_cols = max(ax.col + ax.col_span - 1 for ax in axes)

        # Plotly subplot layouts are defined using a grid of specification
        # dictionaries. Empty dictionaries denote subplot origins, while None
        # marks cells occupied by a spanning subplot.
        specs = [[{}] * num_cols for _ in range(num_rows)]

        # Generate subplots data from axes
        for ax in axes:
            # Ensure no subplot occupies the requested grid location.
            self._check_empty(specs, ax.row, ax.col)
            axes_dict[(ax.row, ax.col)] = ax
            specs[ax.row - 1][ax.col - 1] = {
                "colspan": ax.col_span,
                "rowspan": ax.row_span,
            }
            # Check space available for full row-/col-span
            # Add spec None to covered grid space
            for row in range(ax.row, ax.row + ax.row_span - 1):
                for col in range(ax.col, ax.col + ax.col_span - 1):
                    if row > ax.row or col > ax.col:
                        self._check_empty(specs, row, col)
                        specs[row - 1, col - 1] = None

        # Create figure with supbplots
        make_subplots = self.plotly_manager.make_subplots
        fig = make_subplots(
            rows=num_rows,
            cols=num_cols,
            specs=specs,
            horizontal_spacing=0.2,
            vertical_spacing=0.15,
        )

        # Add axis title to each axis in the subplot
        def _get_axis_title(titles, width, i):
            if isinstance(titles, str):
                title = titles
            elif isinstance(titles, list) and i < len(titles):
                title = titles[i]
            else:
                return None

            return wrap_text(title, width, self.name)

        # Reduce wrapping width as subplot rows increase to avoid overlapping
        # axis titles in dense layouts.
        width = np.floor(50 / num_rows)
        for i, ax in enumerate(axes):
            if title := _get_axis_title(xaxis_titles, width, i):
                fig.update_xaxes(
                    title_text=title,
                    row=ax.row,
                    col=ax.col,
                )
            if title := _get_axis_title(yaxis_titles, width, i):
                fig.update_yaxes(
                    title_text=title,
                    row=ax.row,
                    col=ax.col,
                )

        fig.update_layout(self._figure_layout(style, title))

        return fig, axes_dict, num_rows, num_cols

    def legend(self, fig, style: dict = None):
        """
        Configure and display a figure legend.

        Parameters
        ----------
        fig : plotly.graph_objects.Figure
            Target figure.
        style : dict, optional
            Legend styling options including orientation,
            location and anchor coordinates.
        """
        style = style or {}
        opts = {}
        if style.get("horizontal"):
            opts["orientation"] = "h"
        if "loc" in style:
            anchors = style.get("loc").split(" ")
            if len(anchors) != 2:
                raise ValueError("loc property must consist of 2 keywords")
            opts["xanchor"] = ANCHOR_MAP.get(anchors[1], "auto")
            opts["yanchor"] = ANCHOR_MAP.get(anchors[0], "auto")
        if "coords" in style:
            coords = style.get("coords")
            opts["x"] = coords[0]
            opts["y"] = coords[1]

        fig.update_layout(showlegend=True, legend=opts)

    def show_figure(self, fig):
        """
        Display one or more Plotly figures.

        Parameters
        ----------
        fig : Figure or iterable[Figure]
            Figure or collection of figures to display.
        """
        # Support displaying either a single figure or a collection of figures.
        if hasattr(fig, "__len__") and len(fig) > 0:
            for f in fig:
                f.show()
        else:
            fig.show()

    def plot_trace(self, traces, fig, ax=None):
        """
        Add one or more traces to a figure or subplot.

        Parameters
        ----------
        traces : Trace or list[Trace]
            Plotly trace objects to add.
        fig : plotly.graph_objects.Figure
            Target figure.
        ax : AxisData, optional
            Subplot location. If provided, traces are added
            to the specified subplot.

        Returns
        -------
        None
        """
        for trace in np.atleast_1d(traces):
            if ax is None:
                fig.add_trace(trace)
            else:
                fig.add_trace(trace, row=ax.row, col=ax.col)

    def sample_color_scale(self, data, scale="viridis", d_min=None, d_max=None):
        """
        Sample colours from a Plotly colour scale.

        Parameters
        ----------
        data : array-like
            Values to map onto the colour scale.
        scale : str, optional
            Plotly colour scale name.
        d_min : float, optional
            Minimum value used for normalisation.
        d_max : float, optional
            Maximum value used for normalisation.

        Returns
        -------
        list
            Colours corresponding to the supplied values.
        """
        px = self.plotly_manager.px
        # normalise and clip data
        d_min = d_min or np.nanmin(data[np.isfinite(data)])
        d_max = d_max or np.nanmax(data[np.isfinite(data)])

        d = (data - d_min) / (d_max - d_min)
        if np.isscalar(d):
            d = np.array([d])
        np.clip(np.asarray(d), 0, 1.0, out=d)
        return px.colors.sample_colorscale(scale, list(d))

    def colorbar(self, fig, data, colorscale="viridis", label=None):
        """
        Add a standalone colour bar to a figure.

        Parameters
        ----------
        fig : plotly.graph_objects.Figure
            Target figure.
        data : array-like
            Values defining the colour range.
        colorscale : str, optional
            Plotly colour scale name.
        label : str, optional
            Colour bar title.

        Returns
        -------
        None
        """
        d_min = np.nanmin(data[np.isfinite(data)])
        d_max = np.nanmax(data[np.isfinite(data)])

        colorbar = dict(thickness=25, outlinewidth=1)
        if label is not None:
            colorbar.update({"title": {"text": label, "side": "right"}})

        # Plotly requires a trace to render a standalone colour bar, so an
        # invisible scatter trace is added solely to display the scale.
        fig.add_trace(
            self.plotly_manager.go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                marker=dict(
                    colorscale=colorscale,
                    showscale=True,
                    cmin=d_min,
                    cmax=d_max,
                    colorbar=colorbar,
                ),
                showlegend=False,
                hoverinfo="none",
            )
        )

    def contour_plot(self, x, y, z, colorscale="viridis"):
        """
        Create a contour plot trace.

        Parameters
        ----------
        x, y : array-like
            Coordinate values.
        z : array-like
            Contour values.
        colorscale : str, optional
            Plotly colour scale.

        Returns
        -------
        plotly.graph_objects.Contour
            Contour trace.
        """
        # Use connectgaps=True to ill small gaps in the input grid to avoid breaks in contour regions.
        return self.plotly_manager.go.Contour(
            x=x, y=y, z=z, colorscale=colorscale, connectgaps=True
        )

    def fill(self, x, y, color=None, label=None):
        """
        Create a filled polygon trace.

        Parameters
        ----------
        x, y : array-like
            Polygon coordinates.
        color : str, optional
            Fill colour.
        label : str, optional
            Legend label.

        Returns
        -------
        plotly.graph_objects.Scatter
            Filled polygon trace.
        """
        opts = {}
        if color is not None:
            opts["fillcolor"] = color
        if label is not None:
            opts["name"] = label

        return self.plotly_manager.go.Scatter(
            x=x, y=y, fill="toself", mode="text", showlegend=False, **opts
        )

    def fill_between(self, x, y_upper, y_lower, color):
        """
        Create a filled region between two curves.

        Parameters
        ----------
        x : array-like
            X values.
        y_upper : array-like
            Upper boundary.
        y_lower : array-like
            Lower boundary.
        color : str
            Fill colour.

        Returns
        -------
        plotly.graph_objects.Scatter
            Filled area trace.
        """

        # Construct a closed polygon by traversing the upper curve forwards
        # and the lower curve in reverse.
        return self.plotly_manager.go.Scatter(
            x=x + x[::-1],
            y=y_upper + y_lower[::-1],
            fill="toself",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=False,
            fillcolor=color,
        )

    def histogram_plot(self, x, name, style=None):
        """
        Create a histogram trace.

        Parameters
        ----------
        x : array-like
            Data values.
        name : str
            Histogram label.
        style : dict, optional
            Histogram styling options.

        Returns
        -------
        plotly.graph_objects.Histogram
            Histogram trace.
        """
        style = style or {}

        return self.plotly_manager.go.Histogram(
            x=x, name=name, opacity=style.get("alpha")
        )

    def _get_line_options(self, style, opts):
        """
        Populate Plotly line styling options.

        Parameters
        ----------
        style : dict
            User-supplied style options.
        opts : dict
            Trace options dictionary updated in-place.

        Returns
        -------
        None
        """
        linestyle = style.get("linestyle", "solid")
        color = style.get("color")
        opts["line"] = dict(
            width=style.get("linewidth", 4), dash=LINESTYLE_MAP.get(linestyle, "solid")
        )
        if color is not None:
            opts["line"].update(color=color)

    def line(self, x=None, y=None, label=None, style=None):
        """
        Create a line and/or marker trace.

        Parameters
        ----------
        x : array-like, optional
            X values.
        y : array-like
            Y values.
        label : str, optional
            Legend label.
        style : dict, optional
            Line and marker styling options.
            Currently supported:
                - linestyle: see LINESTYLE_MAP
                - linewidth
                - color
                - marker: the marker symbol see MARKER_MAP
                - markerfacecolor
                - markeredgecolor
                - markeredgewidth
                - fillstyle (for marker)

        Returns
        -------
        plotly.graph_objects.Scatter
            Scatter trace configured as a line, marker plot,
            or combined line-marker plot.
        """

        style = style or {}
        linestyle = style.get("linestyle", "solid")
        marker = style.get("marker", "none")
        opts = {}
        if linestyle.lower() == "none":
            mode = "markers"
        elif marker.lower() == "none":
            mode = "lines"
        else:
            mode = "markers+lines"

        opts["mode"] = mode
        if linestyle.lower() != "none":
            self._get_line_options(style, opts)

        if marker.lower() != "none":
            opts["marker"] = dict(
                size=style.get("markersize", 8),
                symbol=MARKER_MAP.get(marker),
            )
            fillstyle = style.get("fillstyle", "full")
            markerfacecolor = style.get("markerfacecolor")
            markeredgecolor = style.get("markeredgecolor")
            markeredgewidth = style.get("markeredgewidth")

            # Plotly uses "-open" marker variants to represent unfilled markers.
            if fillstyle.lower() == "none":
                opts["marker"].update(symbol=MARKER_MAP.get(marker) + "-open")
                if markeredgecolor is not None:
                    opts["marker"].update(color=markeredgecolor)

            if markerfacecolor is not None:
                opts["marker"].update(color=markerfacecolor)
            if markeredgecolor is not None:
                opts["marker"].update(
                    line_color=markeredgecolor, line_width=markeredgewidth or 1
                )
            elif markeredgewidth is not None:
                opts["marker"].update(line_width=markeredgewidth)

        # Avoid creating empty legend entries for unnamed traces.
        if label is None:
            opts["showlegend"] = False

        kwargs = {"y": y, "name": label, **opts}
        if x is not None:
            kwargs["x"] = x

        return self.plotly_manager.go.Scatter(**kwargs)

    def scatter(self, x, y, colors, labels=None, colorscale="Greys"):
        """
        Create a scatter plot trace.

        Parameters
        ----------
        x, y : array-like
            Point coordinates.
        colors : array-like
            Values used to colour markers.
        labels : array-like, optional
            Hover labels.
        colorscale : str, optional
            Plotly colour scale.

        Returns
        -------
        plotly.graph_objects.Scatter
            Scatter trace.
        """

        opts = dict(
            mode="markers",
            marker=dict(
                color=colors,
                colorscale=colorscale,
                size=8,
                showscale=False,
            ),
            showlegend=False,
        )
        if labels is not None:
            opts.update({"text": labels, "hoverinfo": "text"})
        return self.plotly_manager.go.Scatter(x=x, y=y, **opts)

    def show_table(self, header, values, title):
        """
        Display tabular data as a Plotly table.

        Parameters
        ----------
        header : list
            Column headers.
        values : list
            Table contents.
        title : str
            Table title.

        Returns
        -------
        None
        """
        # Import plotly only when needed

        fig = self.plotly_manager.go.Figure(
            data=[
                self.plotly_manager.go.Table(
                    header=dict(values=header),
                    cells=dict(
                        values=[[row[0] for row in values], [row[1] for row in values]]
                    ),
                )
            ]
        )

        fig.update_layout(title=title)
        fig.show()

    def vline(self, fig, x, style=None):
        """
        Add a vertical reference line to a figure.

        Parameters
        ----------
        fig : plotly.graph_objects.Figure
            Target figure.
        x : float
            X-coordinate of the line.
        style : dict, optional
            Line styling options.

        Returns
        -------
        None
        """
        style = style or {}
        opts = {}
        self._get_line_options(style, opts)
        fig.add_vline(x=x, **opts)
