from __future__ import annotations
# Import PyQt6 modules
from PyQt6.QtWidgets import (
    QMainWindow,
    QDialog,
    QFileDialog,
    QInputDialog,
    QLayout,
    QComboBox,
)
# Import plotting modules
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from agepy import ageplot
# Import internal modules
from agefit.ui import Ui_FitWindow, Ui_LabelDialog, Ui_ParamBox


__all__ = []


class FitWindow(QMainWindow, Ui_FitWindow):
    """Window for the interactive fitting.

    """

    def __init__(
        self,
        backend,
        parent: QMainWindow = None
    ) -> None:
        # Setup the QMainWindow
        super().__init__(parent=parent)
        self.setupUi(self)
        # Set the fitting backend
        self.backend = backend
        # Add matplotlib canvas
        with ageplot.context(["age", "dataviewer"]):
            # Create and add the canvas
            self.canvas = FigureCanvasQTAgg(Figure())
            self.layoutFitView.addWidget(self.canvas)
            # Create the axis
            self.ax = self.canvas.figure.add_subplot(111)
            # Draw the plot
            self.backend.plot_data(self.ax)
            self.ax.set_xlim(*self.ax.get_xlim())
            self.ax.set_ylim(*self.ax.get_ylim())
            self.canvas.draw()
        # Remember the last Line2D objects in order to remove them when
        # updating the prediction
        self.mpl_lines = []
        # Initialize the cost function selection
        available_costs = self.backend.list_costs()
        self.selectCost.addItems(available_costs)
        self.selectCost.setCurrentText(self.backend.which_cost())
        self.selectCost.currentTextChanged.connect(self.change_cost)
        # Initialize the model selection
        available_models = self.backend.list_models()
        if isinstance(available_models, list):
            available_models = {"model": available_models}
        # Get the selected model
        selected_model = self.backend.which_model()
        if isinstance(selected_model, str):
            selected_model = {"model": selected_model}
        # Add the model selection
        self.selectModel = {}
        for model_type in available_models:
            selectModel = QComboBox()
            self.layoutModel.addWidget(selectModel)
            selectModel.addItems(available_models[model_type])
            selectModel.setCurrentText(selected_model[model_type])
            selectModel.currentTextChanged.connect(self.change_model)
            self.selectModel[model_type] = selectModel
        self.change_model()
        # Connect Fit Button
        self.buttonFit.clicked.connect(self.fit)
        # Add the result text box
        self.textResults.setPlainText(self.backend.print_result())
        # Connect the menu actions
        self.actionSetLabels.triggered.connect(self.set_labels)
        self.actionSetTitle.triggered.connect(self.set_title)
        self.actionSaveAs.triggered.connect(self.save_as)
        # Draw the initial model
        self.update_prediction()

    def change_cost(self):
        self.backend.select_cost(self.selectCost.currentText())
        # Update the selected cost in case selecting the new cost failed
        self.selectCost.setCurrentText(self.backend.which_cost())

    def change_model(self):
        # Get the selected models
        selected_model = {}
        for model_type in self.selectModel:
            selected_model[model_type] = self.selectModel[
                model_type].currentText()
        # Pass the selected models to the backend
        self.backend.select_model(**selected_model)
        # Update the selected cost in case the new model does not support
        # the current cost
        self.selectCost.setCurrentText(self.backend.which_cost())
        # Get the new parameters
        params = self.backend.list_params()
        limits = self.backend.list_limits()
        # Clear the current parameters
        self.clear_params(self.layoutParams)
        # Add the new parameters
        self.params = {}
        for par in params:
            # Add group box
            parambox = Ui_ParamBox(par)
            self.layoutParams.addWidget(parambox)
            # Set the values
            val = params[par]
            llimit, ulimit = limits[par]
            parambox.set_value(val)
            parambox.set_limits(llimit, ulimit)
            # Connect signals
            parambox.connect_limits(self.update_limits)
            parambox.connect_value(self.update_backend_params)
            # Save the parameter
            self.params[par] = parambox
        self.layoutParams.addStretch()
        self.update_prediction()

    def clear_params(self, layout: QLayout):
        self.params = {}
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self.clear_params(child_layout)

    def update_limits(self):
        for par in self.params:
            parambox = self.params[par]
            # Get the limits
            llimit, ulimit = parambox.get_limits()
            # Update the limits
            self.backend.set_limits(par, (llimit, ulimit))
            # Adjust the slider limits
            parambox.set_limits(llimit, ulimit)

    def update_backend_params(self, slider_value=None):
        for par in self.params:
            self.backend.set_value(par, self.params[par].get_value())
        self.update_prediction()

    def update_gui_params(self):
        params = self.backend.list_params()
        for par in params:
            self.params[par].set_value(params[par])

    def update_prediction(self):
        # Remove the previous prediction
        for line in self.mpl_lines:
            line.remove()
        # Plot the new prediction
        with ageplot.context(["age", "dataviewer"]):
            self.mpl_lines = self.backend.plot_prediction(self.ax)
            self.canvas.draw_idle()

    def fit(self):
        # Indicate that the fit is running
        self.buttonFit.setEnabled(False)
        # Perform the fit
        self.backend.fit()
        # Indicate that the fit is done
        self.buttonFit.setEnabled(True)
        # Show the fit result
        self.textResults.clear()
        self.textResults.setPlainText(self.backend.print_result())
        # Update the displayed parameters
        self.update_gui_params()
        # Update the prediction
        self.update_prediction()

    def set_labels(self):
        dialog = QDialog(self)
        dialog.ui = Ui_LabelDialog()
        dialog.ui.setupUi(dialog)
        dialog.ui.editXLabel.setText(self.ax.get_xlabel())
        dialog.ui.editYLabel.setText(self.ax.get_ylabel())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            with ageplot.context(["age", "dataviewer"]):
                self.ax.set_xlabel(dialog.ui.editXLabel.text())
                self.ax.set_ylabel(dialog.ui.editYLabel.text())
                self.canvas.draw_idle()

    def set_title(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Set Axes Title")
        dialog.setLabelText("title")
        dialog.setTextValue(self.ax.get_title())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            with ageplot.context(["age", "dataviewer"]):
                self.ax.set_title(dialog.textValue())
                self.canvas.draw_idle()

    def save_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Figure", "",
            "PNG Files (*.png);; PDF Files (*.pdf);;All Files (*)")
        if file_path:
            self.canvas.figure.savefig(file_path)
