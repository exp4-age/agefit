from .__version__ import __version__
from ._agefit import FitWindow
from .backend import GenericFit, SpectrumFit, CalibrationFit

__all__ = [
    "__version__",
    "GenericFit",
    "SpectrumFit",
    "CalibrationFit",
]

import argparse
from PyQt6.QtWidgets import QApplication
import numpy as np


def start():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(
        prog="agefit", description="Start the agefit GUI.")
    parser.add_argument("backend", choices=["spectrum", "calibration"],
                        help="The backend to use.")
    args = parser().parse_args()
    backend = args.backend
    # Create dummy data and initialize the backend
    rng = np.random.default_rng(42)
    if backend == "spectrum":
        xr = (0, 2)
        xdata = rng.normal(1, 0.1, size=1000)
        ydata = rng.exponential(size=len(xdata))
        xmix = np.append(xdata, ydata)
        xmix = xmix[(xr[0] < xmix) & (xmix < xr[1])]
        xe = np.histogram([], bins=20, range=xr)[1]
        backend = SpectrumFit(xe, xmix)
    elif backend == "calibration":
        par_true = np.array((1, 2, 3))

        def f(x, par):
             return np.polyval(par, x)

        data_x = np.linspace(-4, 7, 30)
        data_y = f(data_x, par_true)
        sigma_x = 0.5 * np.ones_like(data_x)
        sigma_y = 5 * np.ones_like(data_y)
        data_x += rng.normal(0, 0.5, 30)
        data_y += rng.normal(0, 5, 30)
        backend = CalibrationFit(data_x, data_y, sigma_y, xerr=sigma_x)
    # Start the GUI
    app = QApplication([])
    window = FitWindow(backend)
    window.show()
    app.exec()
