from PyQt6.QtWidgets import QGroupBox, QGridLayout, QLineEdit
from PyQt6.QtCore import Qt
from agefit.ui import Ui_FloatSlider

class Ui_ParamBox(QGroupBox):
    """Parameter box for the AGE Fit Viewer. It contains a slider and
    line edits for the parameter value and the limits.

    """

    def __init__(self, parameter: str, parent=None) -> None:
        super().__init__(parameter, parent=parent)
        # Add layout
        layout = QGridLayout()
        self.setLayout(layout)
        # Add line edit to display slider value
        self.editValue = QLineEdit()
        # Add value slider
        self.slider = Ui_FloatSlider(Qt.Orientation.Horizontal,
                                  line_edit=self.editValue)
        # Add line edit for changing the limits
        self.editLLimit = QLineEdit()
        self.editULimit = QLineEdit()
        # Add widgets to the layout
        layout.addWidget(self.slider, 0, 0)
        layout.addWidget(self.editValue, 0, 1)
        layout.addWidget(self.editLLimit, 1, 0)
        layout.addWidget(self.editULimit, 1, 1)
        # Add tooltips
        self.slider.setToolTip("Parameter Value")
        self.editValue.setToolTip("Parameter Value")
        self.editLLimit.setToolTip("Lower Limit")
        self.editULimit.setToolTip("Upper Limit")

    def connect_limits(self, callback):
        self.editLLimit.returnPressed.connect(callback)
        self.editULimit.returnPressed.connect(callback)

    def connect_value(self, callback):
        self.slider.floatValueChanged.connect(callback)
        self.editValue.returnPressed.connect(callback)

    def set_limits(self, llimit: float, ulimit: float):
        self.slider.setMinimum(llimit)
        self.slider.setMaximum(ulimit)
        self.editLLimit.setText(str(llimit))
        self.editULimit.setText(str(ulimit))
        # Ensure the slider's value is within the new range
        current_value = self.get_value()
        if current_value < llimit:
            self.slider.setValue(llimit)
            self.editValue.setText(str(llimit))
        elif current_value > ulimit:
            self.slider.setValue(ulimit)
            self.editValue.setText(str(ulimit))
        else:
            self.slider.blockSignals(True)
            self.slider.setValue(llimit)
            self.slider.setValue(current_value)
            self.slider.blockSignals(False)

    def set_value(self, value: float):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.editValue.setText(str(value))
        self.slider.blockSignals(False)

    def get_limits(self) -> tuple[float, float]:
        return float(self.editLLimit.text()), float(self.editULimit.text())

    def get_value(self) -> float:
        return float(self.editValue.text())
