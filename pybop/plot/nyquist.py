from pybop.parameters.parameter import Inputs
from pybop.plot.util import call_plotting_function
from pybop.plot.standard_plots import StandardPlot

def nyquist(problem, inputs: Inputs = None, show=True, backend=None, **layout_kwargs):
    """
    Generates Nyquist plots for the given problem by evaluating the model's output and target values.

    Parameters
    ----------
    problem : pybop.Problem
        An instance of a problem class that contains the parameters and methods
        for evaluation and target retrieval.
    inputs : Inputs, optional
        Input parameters for the problem. If not provided, the default parameters from the problem
        instance will be used. These parameters are verified before use (default is None).
    show : bool, optional
        If True, the plots will be displayed.
    **layout_kwargs : dict, optional
        Additional keyword arguments for customising the plot layout. These arguments are passed to
        `fig.update_layout()`.

    Returns
    -------
    list
        A list of plotly `Figure` objects, each representing a Nyquist plot for the model's output and target values.

    Notes
    -----
    - The function extracts the real part of the impedance from the model's output and the real and imaginary parts
      of the impedance from the target output.
    - For each signal in the problem, a Nyquist plot is created with the model's impedance plotted as a scatter plot.
    - An additional trace for the reference (target output) is added to the plot.
    - The plot layout can be customised using `layout_kwargs`.

    Example
    -------
    >>> problem = pybop.EISProblem()
    >>> nyquist_figures = nyquist(problem, show=True, title="Nyquist Plot", xaxis_title="Real(Z)", yaxis_title="Imag(Z)")
    >>> # The plots will be displayed and nyquist_figures will contain the list of figure objects.
    """
    return call_plotting_function(
        "nyquist", backend, problem=problem, inputs=inputs, show=show, **layout_kwargs
    )

def _nyquist(problem, trace_options_model: dict, trace_options_reference, inputs: Inputs = None):

    if not isinstance(inputs, dict):
        inputs = problem.parameters.to_dict(inputs)

    model_output = problem.simulate(inputs)
    domain_data = model_output["Impedance"].data.real
    target_output = problem.target_data
    figure_list = []
    for var in problem.target:
        plot_dict = StandardPlot(
                x=domain_data,
                y=-model_output[var].data.imag,
                trace_names="Model",
        )

        plot_dict.traces[0].update(trace_options_model)

        target_trace = plot_dict.create_trace(
            x=target_output[var].real,
            y=-target_output[var].imag,
            **trace_options_reference,
        )
        plot_dict.traces.append(target_trace)

        fig = plot_dict(show=False)
        figure_list.append(fig)

    return figure_list
