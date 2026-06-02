import numpy as np

from pybop.plot.backends.base import PlotBackend
from pybop.plot.backends.plotly_manager import PlotlyManager
from pybop.plot.util import AxisData, wrap_text

LINESTYLE_MAP = {
    "solid": "solid",
    "dashed": "dash",
    "dotted": "dot",
    "dashdot": "dashdot",
}

MARKER_MAP = {"o": "circle", "P": "cross", "X": "x", ".": None}

ANCHOR_MAP = {
    "lower": "bottom",
    "upper": "top",
    "left": "left",
    "center": "center",
    "right": "right",
}


class PlotlyBackend(PlotBackend):
    def __init__(self):
        self.name = "plotly"
        self.plotly_manager = PlotlyManager()

    def create_figure(
        self, title=None, xaxis_title=None, yaxis_title=None, traces=None, style=None
    ):
        style = style or {}

        layout = self.plotly_manager.go.Layout(
            {
                "title": title,
                "xaxis_title": xaxis_title,
                "yaxis_title": yaxis_title,
                "width": style.get("width"),
                "height": style.get("height"),
                "xaxis_range": style.get("xaxis_range"),
                "yaxis_range": style.get("yaxis_range"),
                "xaxis": dict(
                    title=dict(font={"size": 14}),
                    showexponent="last",
                    exponentformat="e",
                    tickfont=dict(size=12),
                ),
                "yaxis": dict(
                    title=dict(font={"size": 14}),
                    showexponent="last",
                    exponentformat="e",
                    tickfont=dict(size=12),
                ),
                "plot_bgcolor": style.get("bg_color"),
                "barmode": "overlay",
            }
        )
        fig = self.plotly_manager.go.Figure(data=traces, layout=layout)
        return fig

    def _check_empty(self, specs, row, col):
        if specs[row - 1][col - 1] is None or len(specs[row - 1][col - 1]) > 0:
            raise ValueError("Overlapping axes are not supported")

    def make_subplots(
        self,
        axes: list[AxisData],
        title=None,
        axis_titles_x: list[str] | str = None,
        axis_titles_y: list[str] | str = None,
        style=None,
    ):
        style = style or {}

        num_rows = max(ax.row + ax.row_span - 1 for ax in axes)
        num_cols = max(ax.col + ax.col_span - 1 for ax in axes)
        specs = [[{}] * num_cols for _ in range(num_rows)]
        axes_dict = {}

        for ax in axes:
            self._check_empty(specs, ax.row, ax.col)
            axes_dict[(ax.row, ax.col)] = ax
            specs[ax.row - 1][ax.col - 1] = {
                "colspan": ax.col_span,
                "rowspan": ax.row_span,
            }
            for row in range(ax.row, ax.row + ax.row_span - 1):
                for col in range(ax.col, ax.col + ax.col_span - 1):
                    if row > ax.row or col > ax.col:
                        self._check_empty(specs, row, col)
                        specs[row - 1, col - 1] = None

        make_subplots = self.plotly_manager.make_subplots
        fig = make_subplots(
            rows=num_rows,
            cols=num_cols,
            specs=specs,
            horizontal_spacing=0.2,
            vertical_spacing=0.15,
        )

        for i, ax in enumerate(axes):
            if isinstance(axis_titles_x, str):
                fig.update_xaxes(
                    title_text=wrap_text(
                        axis_titles_x, np.floor(50 / num_rows), self.name
                    ),
                    row=ax.row,
                    col=ax.col,
                )
            elif isinstance(axis_titles_x, list) and i < len(axis_titles_x):
                fig.update_xaxes(
                    title_text=wrap_text(
                        axis_titles_x[i], np.floor(50 / num_rows), self.name
                    ),
                    row=ax.row,
                    col=ax.col,
                )
            if isinstance(axis_titles_y, str):
                fig.update_yaxes(
                    title_text=wrap_text(
                        axis_titles_y, np.floor(50 / num_rows), self.name
                    ),
                    row=ax.row,
                    col=ax.col,
                )
            elif isinstance(axis_titles_y, list) and i < len(axis_titles_y):
                fig.update_yaxes(
                    title_text=wrap_text(
                        axis_titles_y[i], np.floor(50 / num_rows), self.name
                    ),
                    row=ax.row,
                    col=ax.col,
                )

        fig.update_layout(
            {
                "title": title,
                "width": style.get("width"),
                "height": style.get("height"),
                "xaxis": dict(
                    title=dict(font={"size": 14}),
                    showexponent="last",
                    exponentformat="e",
                    tickfont=dict(size=12),
                ),
                "yaxis": dict(
                    title=dict(font={"size": 14}),
                    showexponent="last",
                    exponentformat="e",
                    tickfont=dict(size=12),
                ),
                "plot_bgcolor": style.get("bg_color"),
            }
        )

        return fig, axes_dict, num_rows, num_cols

    def legend(self, fig, style: dict = None):
        style = style or {}
        opts = {}
        if style.get("horizontal"):
            opts["orientation"] = "h"
        if "loc" in style.keys():
            anchors = style.get("loc").split(" ")
            if len(anchors) != 2:
                raise ValueError("loc property must consist of 2 keywords")
            opts["xanchor"] = ANCHOR_MAP.get(anchors[1], "auto")
            opts["yanchor"] = ANCHOR_MAP.get(anchors[0], "auto")
        if "coords" in style.keys():
            coords = style.get("coords")
            opts["x"] = coords[0]
            opts["y"] = coords[1]

        fig.update_layout(showlegend=True, legend=opts)

    def show_figure(self, fig):
        if hasattr(fig, "__len__") and len(fig) > 0:
            for f in fig:
                f.show()
        else:
            fig.show()

    def plot_trace(self, traces, fig, ax=None):
        if not isinstance(traces, list):
            traces = [traces]
        for trace in traces:
            if ax is None:
                fig.add_trace(trace)
            else:
                fig.add_trace(trace, row=ax.row, col=ax.col)

    def sample_color_scale(self, data, scale="viridis", d_min=None, d_max=None):
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

        d_min = np.nanmin(data[np.isfinite(data)])
        d_max = np.nanmax(data[np.isfinite(data)])

        colorbar = dict(thickness=25, outlinewidth=1)
        if label is not None:
            colorbar.update({"title": {"text": label, "side": "right"}})
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

        return self.plotly_manager.go.Contour(
            x=x, y=y, z=z, colorscale=colorscale, connectgaps=True
        )

    def _get_line_options(self, style, opts):
        linestyle = style.get("linestyle", "solid")
        color = style.get("color")
        opts["line"] = dict(
            width=style.get("linewidth", 4), dash=LINESTYLE_MAP.get(linestyle, "solid")
        )
        if color is not None:
            opts["line"].update(color=color)

    def fill_plot(self, x, y, color=None, label=None):
        opts = {}
        if color is not None:
            opts["fillcolor"] = color
        if label is not None:
            opts["name"] = label

        return self.plotly_manager.go.Scatter(
            x=x, y=y, fill="toself", mode="text", showlegend=False, **opts
        )

    def fill_between_plot(self, x, y_upper, y_lower, color):

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
        style = style or {}

        return self.plotly_manager.go.Histogram(
            x=x, name=name, opacity=style.get("alpha")
        )

    def line(self, x=None, y=None, label=None, style=None):

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
            if fillstyle.lower() == "none":
                opts["marker"].update(symbol=MARKER_MAP.get(marker) + "-open")
                if markeredgecolor is not None:
                    opts["marker"].update(color=markeredgecolor)

            if markerfacecolor is not None:
                opts["marker"].update(color=markerfacecolor)
            if markeredgecolor is not None:
                opts["marker"].update(
                    line_color=markeredgecolor, line_width=1 or markeredgewidth
                )
            elif markeredgewidth is not None:
                opts["marker"].update(line_width=markeredgewidth)

        if label is None:
            opts["showlegend"] = False

        if x is not None and y is not None:
            return self.plotly_manager.go.Scatter(
                x=x,
                y=y,
                name=label,
                **opts,
            )
        if x is None and y is not None:
            return self.plotly_manager.go.Scatter(
                y=y,
                name=label,
                **opts,
            )

    def scatter_plot(self, x, y, colors, labels=None, colorscale="Greys"):

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
        Display data in a table.
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

    def add_vline(self, fig, x, style=None):
        style = style or {}
        opts = {}
        self._get_line_options(style, opts)
        fig.add_vline(x=x, **opts)
