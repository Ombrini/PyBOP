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
    'parameters' : dict(figsize=(18, 8), title="Parameter Convergence"),
    'problem' : { 
        'default_trace_options' : dict (label="Model", marker=None, linestyle='-'),
        'design_cost_options' : dict(label = "Optimised"),
        'meta_problem_options' : dict(marker=".", linestyle='none'),
        'reference_options' : dict(label="Reference", marker=".", linestyle='none'), 
        'fill_options' : dict(color=[(1.0, 0.898, 0.800, 0.8)])  
    }
}