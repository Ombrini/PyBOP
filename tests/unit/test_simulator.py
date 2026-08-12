from copy import copy

import numpy as np
import pybamm
import pytest

import pybop
from pybop.simulators.base_simulator import BaseSimulator


class TestSimulator:
    """
    A class to test the BaseSimulator class.
    """

    pytestmark = pytest.mark.unit

    def test_parameter_errors_constructor(self):
        params = {
            "Negative particle radius [m]": pybop.Parameter(
                pybop.Gaussian(2e-05, 1e-6, truncated_at=[1e-6, 5e-5])
            ),
            "Positive particle radius [m]": pybop.Parameter(
                pybop.Gaussian(0.5e-05, 1e-6, truncated_at=[1e-6, 5e-5])
            ),
        }

        simulator = BaseSimulator(copy(params))
        for key in params.keys():
            assert simulator.parameters[key] is params[key]
        # Check that pybop.Parameter objects are removed from the dictionary
        simulator = BaseSimulator(params)
        for key in params.keys():
            assert params[key] == "[input]"

        params = {
            "Negative particle radius [m]": (
                pybop.Gaussian(2e-05, 0.1e-5, truncated_at=[1e-6, 5e-5])
            ),
            "Positive particle radius [m]": (
                pybop.Gaussian(0.5e-05, 0.1e-5, truncated_at=[1e-6, 5e-5])
            ),
        }

        simulator = BaseSimulator(copy(params))
        assert len(simulator.parameters) == 0

        params = [
            pybop.Parameter(pybop.Gaussian(2e-05, 1e-6, truncated_at=[1e-6, 5e-5])),
            pybop.Parameter(pybop.Gaussian(2e-05, 1e-6, truncated_at=[1e-6, 5e-5])),
        ]

        with pytest.raises(
            TypeError,
            match="Parameters must be a dictionary of pybop.Parameter objects or a pybop.Parameters object.",
        ):
            BaseSimulator(params)


class TestPybammSimulator:
    """
    A class to test the pybamm.Simulator class.
    """

    pytestmark = pytest.mark.unit

    def test_set_output_variables(self):
        model = pybamm.lithium_ion.SPM()
        parameter_values = model.default_parameter_values
        experiment = pybamm.Experiment(
            ["Discharge at 1C for 5 minutes (10 second period)"]
        )

        simulator = pybop.pybamm.Simulator(
            model, parameter_values=parameter_values, protocol=experiment
        )

        with pytest.raises(
            ValueError, match="Not a variable is not a variable in the model."
        ):
            simulator.set_output_variables(["Not a variable"])


class TestOperandoEISSimulator:
    """
    A class to test the operando mode of the pybamm.EISSimulator class.
    """

    pytestmark = pytest.mark.unit

    @pytest.fixture
    def setup(self):
        model = pybamm.lithium_ion.SPM(
            options={"surface form": "differential", "contact resistance": "true"}
        )
        parameter_values = pybamm.ParameterValues("Chen2020")
        parameter_values["Contact resistance [Ohm]"] = 0.0
        parameter_values.set_initial_state(0.9)

        time = np.arange(0, 601, 10.0)
        f_eval = np.logspace(-1, 3, 4)
        columns = pybop.pybamm.eis_column_names(f_eval)

        # Two spectra: one at the start, one part-way through the rest
        eis_rows = [0, 40]
        data = {
            "Time [s]": time,
            "Current [A]": np.zeros_like(time),
            "Voltage [V]": np.zeros_like(time),
        }
        for name in columns:
            column = np.zeros(len(time))
            column[eis_rows] = 1.0
            data[name] = column

        dataset = pybop.Dataset(data, domain="Time [s]")
        return model, parameter_values, dataset, f_eval, columns, eis_rows

    def test_output_shape_and_zero_padding(self, setup):
        model, parameter_values, dataset, f_eval, columns, eis_rows = setup
        simulator = pybop.pybamm.EISSimulator(
            model, parameter_values=parameter_values, protocol=dataset, f_eval=f_eval
        )
        solution = simulator.solve()

        n_time = len(dataset["Time [s]"])
        assert len(solution["Voltage [V]"].data) == n_time
        for name in columns:
            data = solution[name].data
            assert len(data) == n_time
            # Non-zero only at the times of acquisition
            np.testing.assert_array_equal(np.flatnonzero(data), eis_rows)

    def test_matches_stationary_at_initial_state(self, setup):
        """The spectrum at t=0 must match a stationary simulation of the same state."""
        model, parameter_values, dataset, f_eval, columns, _ = setup
        operando = pybop.pybamm.EISSimulator(
            model, parameter_values=parameter_values, protocol=dataset, f_eval=f_eval
        ).solve()
        stationary = pybop.pybamm.EISSimulator(
            model, parameter_values=parameter_values, f_eval=f_eval
        ).solve()

        impedance = np.asarray(
            [
                operando[columns[2 * j]].data[0]
                + 1j * operando[columns[2 * j + 1]].data[0]
                for j in range(len(f_eval))
            ]
        )
        np.testing.assert_allclose(impedance, stationary["Impedance"].data, rtol=1e-10)

    def test_builds_once(self, setup):
        """The model and the constant matrices are set up once, not per evaluation."""
        model, parameter_values, dataset, f_eval, _, _ = setup
        parameter_values["Negative electrode active material volume fraction"] = (
            pybop.Parameter(pybop.Uniform(0.4, 0.75))
        )
        simulator = pybop.pybamm.EISSimulator(
            model, parameter_values=parameter_values, protocol=dataset, f_eval=f_eval
        )

        calls = {"create": 0, "set_up": 0}
        original_create = simulator._simulator.create_simulation
        original_set_up = simulator._set_up_matrices

        def counted_create(*args, **kwargs):
            calls["create"] += 1
            return original_create(*args, **kwargs)

        def counted_set_up(*args, **kwargs):
            calls["set_up"] += 1
            return original_set_up(*args, **kwargs)

        simulator._simulator.create_simulation = counted_create
        simulator._set_up_matrices = counted_set_up

        inputs = {"Negative electrode active material volume fraction": 0.6}
        for _ in range(3):
            simulator.solve(inputs)

        assert calls["create"] == 0  # built during construction
        assert calls["set_up"] == 1

    def test_column_names_round_trip(self):
        f_eval = np.logspace(-2, 4, 5)
        columns = pybop.pybamm.eis_column_names(f_eval)
        # Names may reach the parser in any order, e.g. via a set
        frequencies, real, imaginary = pybop.pybamm.parse_eis_column_names(
            ["Voltage [V]", *reversed(columns)]
        )
        np.testing.assert_allclose(frequencies, f_eval, rtol=1e-6)
        assert real == columns[::2]
        assert imaginary == columns[1::2]

        # No impedance columns present
        frequencies, real, imaginary = pybop.pybamm.parse_eis_column_names(
            ["Voltage [V]", "Current [A]"]
        )
        assert len(frequencies) == 0 and real == [] and imaginary == []

    def test_dataset_errors(self, setup):
        model, parameter_values, dataset, f_eval, columns, _ = setup

        with pytest.raises(ValueError, match="missing impedance columns"):
            pybop.pybamm.EISSimulator(
                model,
                parameter_values=parameter_values,
                protocol=dataset,
                f_eval=np.append(f_eval, 1e4),
            )

        for name in columns:
            dataset[name] = np.zeros(len(dataset["Time [s]"]))
        with pytest.raises(ValueError, match="zero everywhere"):
            pybop.pybamm.EISSimulator(
                model,
                parameter_values=parameter_values,
                protocol=dataset,
                f_eval=f_eval,
            )
