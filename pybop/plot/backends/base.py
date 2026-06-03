from abc import ABC, abstractmethod

from pybop.plot.util import AxisData


class PlotBackend(ABC):
    """
    Abstract base class defining a plotting backend interface.

    Concrete implementations provide plotting functionality for a specific
    visualization library (e.g. Plotly, Matplotlib) while exposing a common
    API to the rest of the application.

    Methods in this interface are responsible for creating figures, adding
    traces and annotations, generating specialised plot types, and rendering
    results.
    """

    @abstractmethod
    def create_figure(
        self,
        title: str = None,
        xaxis_title: str = None,
        yaxis_title: str = None,
        traces: list = None,
        style: dict = None,
    ):
        """
        Create and return a new figure.

        Parameters
        ----------
        title : str, optional
            Figure title.
        xaxis_title : str, optional
            X-axis label.
        yaxis_title : str, optional
            Y-axis label.
        traces : list, optional
            Initial traces to add to the figure.
        style : dict, optional
            Backend-specific styling options.

        Returns
        -------
        object
            Backend-specific figure object.
        """
        raise NotImplementedError

    @abstractmethod
    def make_subplots(
        self,
        axes: list[AxisData],
        title=None,
        xaxis_titles: list[str] | str = None,
        yaxis_titles: list[str] | str = None,
        style=None,
    ):
        """
        Create a figure containing multiple subplot axes.

        Parameters
        ----------
        axes : list[AxisData]
            Definitions describing subplot layout and configuration.
        title : str, optional
            Figure title.
        xaxis_titles : str or list[str], optional
            X-axis titles for each subplot.
        yaxis_titles : str or list[str], optional
            Y-axis titles for each subplot.
        style : dict, optional
            Backend-specific styling options.

        Returns
        -------
        object
            Backend-specific figure object.
        """
        raise NotImplementedError

    @abstractmethod
    def legend(self, fig, style: dict = None):
        """
        Configure or display a legend for a figure.

        Parameters
        ----------
        fig : object
            Figure object.
        style : dict, optional
            Legend styling options.
        """
        raise NotImplementedError

    @abstractmethod
    def show_figure(self, fig):
        """
        Render or display a figure.

        Parameters
        ----------
        fig : object
            Figure to display.
        """
        raise NotImplementedError

    @abstractmethod
    def plot_trace(self, traces: dict | list[dict], fig, ax=None, color_cycle=None):
        """
        Add one or more traces to a figure or subplot.

        Parameters
        ----------
        traces : dict or list[dict]
            Trace definitions to plot.
        fig : object
            Target figure.
        ax : object, optional
            Target subplot axis.
        color_cycle : iterable, optional
            Sequence of colours used when plotting multiple traces.
        """
        raise NotImplementedError

    @abstractmethod
    def sample_color_scale(self, data, scale="viridis", d_min=None, d_max=None):
        """
        Map data values onto a colour scale.

        Parameters
        ----------
        data : array-like
            Values to colour-map.
        scale : str, optional
            Colour scale name.
        d_min : float, optional
            Lower bound for normalisation.
        d_max : float, optional
            Upper bound for normalisation.

        Returns
        -------
        array-like
            Colours corresponding to the supplied data.
        """
        raise NotImplementedError

    @abstractmethod
    def colorbar(self, fig, data, colorscale="viridis", label=None):
        """
        Add a colour bar representing a colour scale.

        Parameters
        ----------
        fig : object
            Target figure.
        data : array-like
            Data used for colour scaling.
        colorscale : str, optional
            Colour scale name.
        label : str, optional
            Colour bar label.
        """
        raise NotImplementedError

    @abstractmethod
    def contour_plot(self, x, y, z, colorscale="viridis"):
        """
        Create a contour plot.

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
            Backend-specific contour trace or figure.
        """
        raise NotImplementedError

    @abstractmethod
    def fill(self, x, y, color=None, label=None):
        """
        Create a filled region plot.

        Parameters
        ----------
        x, y : array-like
            Coordinates defining the filled area.
        color : str, optional
            Fill colour.
        label : str, optional
            Legend label.
        """
        raise NotImplementedError

    @abstractmethod
    def fill_between(self, x, y_upper, y_lower, color):
        """
        Create a filled region between upper and lower bounds.

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
        raise NotImplementedError

    @abstractmethod
    def histogram_plot(self, x, name, style=None):
        """
        Create a histogram.

        Parameters
        ----------
        x : array-like
            Data to bin.
        name : str
            Histogram label.
        style : dict, optional
            Histogram styling options.
        """
        raise NotImplementedError

    @abstractmethod
    def line(self, x=None, y=None, label=None, style=None):
        """
        Create a line plot trace.

        Parameters
        ----------
        x, y : array-like, optional
            Coordinates of the line.
        label : str, optional
            Trace label.
        style : dict, optional
            Line styling options.

        Returns
        -------
        object
            Backend-specific line trace.
        """
        raise NotImplementedError

    @abstractmethod
    def scatter(self, x, y, colors, labels=None, colorscale="Greys"):
        """
        Create a scatter plot.

        Parameters
        ----------
        x, y : array-like
            Point coordinates.
        colors : array-like
            Values or colours associated with each point.
        labels : array-like, optional
            Point labels.
        colorscale : str, optional
            Colour scale name.
        """
        raise NotImplementedError

    @abstractmethod
    def show_table(self, header, values, title):
        """
        Display tabular data.

        Parameters
        ----------
        header : list
            Column headers.
        values : list
            Table contents.
        title : str
            Table title.
        """
        raise NotImplementedError

    @abstractmethod
    def vline(self, fig, x, style=None):
        """
        Add a vertical reference line to a figure.

        Parameters
        ----------
        fig : object
            Target figure.
        x : float
            X-coordinate of the line.
        style : dict, optional
            Line styling options.
        """
        raise NotImplementedError
