from typing import TYPE_CHECKING
import warnings

from matplotlib import pyplot as plt

if TYPE_CHECKING:
    from pybop.samplers.base_pints_sampler import SamplingResult


def trace(result: "SamplingResult", show=True, **kwargs):
    """
    Plot trace plots for the posterior samples.
    """
    # Warning if layout arguments ignored
    if len(kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )
    figlist = []
    for i in range(result.n_parameters):
        fig = plt.figure()

        for j, chain in enumerate(result.chains):
            plt.plot(chain[:, i], label=f"Chain {j}")

        plt.title(f"Parameter {i} Trace Plot")
        plt.xlabel("Sample Index")
        plt.ylabel("Value")
        plt.legend(fontsize=12)
        figlist.append(fig)


    if show:
        plt.show()
    else:
        return figlist



def chains(result: "SamplingResult", show=True, **kwargs):
    """
    Plot posterior distributions for each chain.
    """
    # Warning if layout arguments ignored
    if len(kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )
    fig = plt.figure(figsize=(15, 8), dpi=100)

    for i, chain in enumerate(result.chains):
        for j in range(chain.shape[1]):
            plt.hist(
                x=chain[:, j],
                label=f"Chain {i} - Parameter {j}",
                alpha=0.5,
                rwidth=2.0
            )

    for j in range(chain.shape[1]):
        plt.plot([result.mean[j], result.mean[j]], [0, result.max[j]],"--", lw=3, label=f"Mean - Parameter {j}")

    plt.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    plt.grid(axis='y', zorder=-1)
    plt.title("Posterior Distribution")
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.tight_layout()
    if show:
        plt.show()
    else:
        return fig

def posterior(result: "SamplingResult", show=True, **kwargs):
    """
    Plot the summed posterior distribution across chains.
    """
    # Warning if layout arguments ignored
    if len(kwargs) > 0:
        warnings.warn(
            "The following layout argument keys are ignored for the current plotting backend (matplotlib): \n"
            f"{list(kwargs.keys())}",
            UserWarning,
            stacklevel=2,
        )

    fig = plt.figure(figsize=(15, 8), dpi=100)

    for j in range(result.all_samples.shape[1]):
        plt.hist(
            x=result.all_samples[:, j],
            label=f"Parameter {j}",
            alpha=0.75,
        )
        plt.axvline(result.mean[j], ls='--', c='k', lw=3)

    plt.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    plt.grid(axis='y', zorder=-1)
    plt.title("Posterior Distribution")
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.tight_layout()
    if show:
        plt.show()
    else:
        return fig


def summary_table(result: "SamplingResult"):
    """
    Display summary statistics in a table.
    """

    summary_stats = result.get_summary_statistics()

    header = ["Statistic", "Value"]
    values = [
        ["Mean", ', '.join(summary_stats["mean"].astype(str))],
        ["Median", ', '.join(summary_stats["median"].astype(str))],
        ["Standard Deviation", ', '.join(summary_stats["std"].astype(str))],
        ["95% CI Lower", ', '.join(summary_stats["ci_lower"].astype(str))],
        ["95% CI Upper", ', '.join(summary_stats["ci_upper"].astype(str))],
    ]
    fig, ax = plt.subplots(figsize=(6, 2), dpi=100)

    # hide axes
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=values, colLabels=header, loc='center', cellLoc='center', colColours=['lightsteelblue', 'lightsteelblue'])
    ax.set_title("Summary Statistics")
    fig.tight_layout()
    plt.show()
