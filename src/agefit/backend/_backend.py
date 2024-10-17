from __future__ import annotations
from typing import TYPE_CHECKING
from PyQt6.QtWidgets import QApplication
from agefit import FitWindow
if TYPE_CHECKING:
    from typing import Union, Sequence, Dict, Tuple
    from PyQt6.QtWidgets import QMainWindow
    from matplotlib.axes import Axes
    from matplotlib.lines import Line2D

__all__ = []


class GenericFit:
    """Dummy class for the fitting logic. Most methods need to be
    overwritten by a subclass.

    """

    def __init__(self) -> None:
        self._models = {"model": {"Not implemented!": None}}
        self.select_model("Not implemented!")
        self.select_cost("Not implemented!")

    def interactive(self, parent: QMainWindow = None) -> None:
        """Start the fitting GUI.

        Parameters
        ----------
        parent : QMainWindow, optional
            If no parent is given, a new QApplication is created.

        """
        # Create the window
        window = FitWindow(self, parent=parent)
        # Start the GUI
        if parent is None:
            app = QApplication([])
            window.show()
            app.exec()
        else:
            window.show()

    def list_costs(self) -> Sequence[str]:
        return ["Not implemented!"]

    def which_cost(self) -> str:
        return self._cost_name

    def select_cost(self, name: str) -> None:
        self._cost_name = name

    def list_models(self) -> Dict[str, Sequence[str]]:
        models = {}
        for model_type in self._models:
            models[model_type] = list(self._models[model_type].keys())
        return models

    def which_model(self) -> Union[str, Dict[str, str]]:
        return self._model_name

    def select_model(self, model: str) -> None:
        self._model_name = model
        self._model = self._models["model"][model]
        self._params = {"Not implemented!": 0}
        self._limits = {"Not implemented!": (-1, 1)}

    def get_model(self) -> callable:
        return self._model

    def list_params(self) -> Dict[str, float]:
        return self._params

    def list_limits(self) -> Dict[str, Tuple[float, float]]:
        return self._limits

    def value(self, name: str) -> float:
        if name not in self.list_params():
            raise ValueError(f"Parameter {name} not available.")
        return self._params[name]

    def set_value(self, name: str, value: float) -> None:
        if name not in self.list_params():
            raise ValueError(f"Parameter {name} not available.")
        self._params[name] = value
        self._cov = None

    def set_limits(self, name: str, limits: Tuple[float, float]) -> None:
        if name not in self.list_params():
            raise ValueError(f"Parameter {name} not available.")
        self._limits[name] = limits

    def fit(self) -> None:
        pass

    def plot_data(self, ax: Axes) -> None:
        ax.set_title("AGE Fit")

    def plot_prediction(self, ax: Axes) -> Sequence[Line2D]:
        return []

    def print_result(self) -> str:
        return "Not implemented!"
