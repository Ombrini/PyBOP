from abc import ABC, abstractmethod
from pybop.plot.util import _AxisData

class PlotBackend(ABC):
    @abstractmethod
    def create_figure(self, title: str=None, xaxis_title: str=None, yaxis_title: str=None, traces: list=None, style:dict=None):
        raise NotImplementedError
    
    @abstractmethod
    def make_subplots(self, axes: list[_AxisData], title=None, axis_titles_x: list[str] | str = None, axis_titles_y: list[str] | str = None, style=None):
        raise NotImplementedError
    
    @abstractmethod
    def legend(self, fig, style: dict=None):
        raise NotImplementedError
    
    @abstractmethod
    def show_figure(self, fig):
        raise NotImplementedError
    
    @abstractmethod
    def plot_trace(self, traces: dict | list[dict], fig, ax=None, color_cycle=None):
        raise NotImplementedError
    
    @abstractmethod
    def sample_color_scale(self, data, scale="viridis", d_min=None, d_max=None):
        raise NotImplementedError
    
    @abstractmethod
    def colorbar(self, fig, data, colorscale="viridis", label=None):
        raise NotImplementedError
    
    @abstractmethod
    def contour_plot(self, x, y, z, colorscale="viridis"):
        raise NotImplementedError
    
    @abstractmethod
    def fill_plot(self, x, y, color=None, label=None):
        raise NotImplementedError
    
    @abstractmethod
    def fill_between_plot(self, x, y_upper, y_lower, color):
        raise NotImplementedError
    
    @abstractmethod
    def histogram_plot(self, x, name, style=None):
        raise NotImplementedError
    
    @abstractmethod
    def line_plot(self, x=None, y=None, label=None, style = None):
        raise NotImplementedError
    
    @abstractmethod
    def scatter_plot(self, x, y, colors, labels=None, colorscale="Greys"):
        raise NotImplementedError
    
    @abstractmethod
    def show_table(self, header, values, title):
        raise NotImplementedError
    
    @abstractmethod
    def add_vline(self, fig, x, style=None):
        raise NotImplementedError

    


    

    
