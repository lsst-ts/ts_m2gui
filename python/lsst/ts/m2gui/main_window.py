# This file is part of ts_m2gui.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["MainWindow"]

import logging
import sys

from PySide2 import QtCore
from PySide2.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
)

from .utils import set_button
from . import Model, ControlTabs
from .signal import SignalControl
from .layout import LayoutControl, LayoutLocalMode, LayoutControlMode


class MainWindow(QMainWindow):
    """Main window of the application.

    Parameters
    ----------
    is_output_log_on_screen : `bool`
        Is outputting the log messages on screen or not.
    log : `logging.Logger` or None, optional
        A logger. If None, a logger will be instantiated. (the default is
        None)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    model : `Model`
        Model class.
    """

    def __init__(self, is_output_log_on_screen, log=None):
        super().__init__()

        # Set the logger
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        if is_output_log_on_screen:
            logging.basicConfig(
                level=logging.INFO,
                handlers=[logging.StreamHandler(sys.stdout)],
                format="%(asctime)s, %(name)s, %(levelname)s, %(message)s",
            )

        self.model = Model(self.log)

        # Singal of control
        self._signal_control = SignalControl()

        # Layout of the control panel
        self._layout_control = LayoutControl(self.model, self.log, self._signal_control)

        # Layout of the local mode
        self._layout_local_mode = LayoutLocalMode(
            self.model, self.log, self._signal_control
        )

        # Layout of the control mode
        self._layout_control_mode = LayoutControlMode(
            self.model, self.log, self._signal_control
        )

        # Control tables
        self._control_tabs = ControlTabs(self.log)

        # Set the main window of application
        self.setWindowTitle("M2 Control")

        # Set the central widget of the Window
        container = QWidget()
        container.setLayout(self._create_layout())
        self.setCentralWidget(container)

        # Set the default conditions
        self._layout_control.set_csc_commander(True)

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addLayout(self._layout_control.layout)
        layout.addLayout(self._layout_local_mode.layout)
        layout.addLayout(self._layout_control_mode.layout)
        layout.addWidget(self._control_tabs)

        button_exit = set_button("Exit", self._callback_exit)
        layout.addWidget(button_exit)

        return layout

    @QtCore.Slot()
    def _callback_exit(self):
        """Exit the application."""

        app = QtCore.QCoreApplication.instance()
        app.quit()
