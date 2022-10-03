# This file is part of ts_m2gui.
#
# Developed for the LSST Telescope and Site Systems.
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

__all__ = ["TabSettings"]

from PySide2.QtWidgets import QFormLayout, QLineEdit, QSpinBox, QVBoxLayout
from qasync import QApplication, asyncSlot

from ..utils import create_group_box, run_command, set_button
from . import TabDefault


class TabSettings(TabDefault):
    """Table of the settings.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    PORT_MINIMUM = 1
    PORT_MAXIMUM = 65535

    LOG_LEVEL_MINIMUM = 10
    LOG_LEVEL_MAXIMUM = 50

    # The unit is seconds
    TIMEOUT_MINIMUM = 1

    # The unit is Hz
    REFRESH_FREQUENCY_MINIMUM = 1
    REFRESH_FREQUENCY_MAXIMUM = 10

    POINT_SIZE_MINIMUM = 9
    POINT_SIZE_MAXIMUM = 14

    def __init__(self, title, model):
        super().__init__(title, model)

        self._settings = self._create_settings()

        self._button_apply_host = set_button(
            "Apply Host Settings", self._callback_apply_host
        )
        self._button_apply_general = set_button(
            "Apply General Settings", self._callback_apply_general
        )

        # Internal layout
        self.widget().setLayout(self._create_layout())

    def _create_settings(self):
        """Create the settings.

        Returns
        -------
        `dict`
            Settings.
        """

        settings = {
            "host": QLineEdit(),
            "port_command": QSpinBox(),
            "port_telemetry": QSpinBox(),
            "timeout_connection": QSpinBox(),
            "log_level": QSpinBox(),
            "refresh_frequency": QSpinBox(),
            "point_size": QSpinBox(),
        }

        for port in ("port_command", "port_telemetry"):
            settings[port].setRange(self.PORT_MINIMUM, self.PORT_MAXIMUM)

        settings["timeout_connection"].setMinimum(self.TIMEOUT_MINIMUM)
        settings["timeout_connection"].setSuffix(" sec")

        settings["log_level"].setRange(self.LOG_LEVEL_MINIMUM, self.LOG_LEVEL_MAXIMUM)
        settings["log_level"].setToolTip(
            "CRITICAL (50), ERROR (40), WARNING (30), INFO (20), DEBUG (10)"
        )

        settings["refresh_frequency"].setRange(
            self.REFRESH_FREQUENCY_MINIMUM, self.REFRESH_FREQUENCY_MAXIMUM
        )
        settings["refresh_frequency"].setSuffix(" Hz")
        settings["refresh_frequency"].setToolTip(
            "Frequency to refresh the data on tables"
        )

        settings["point_size"].setRange(
            self.POINT_SIZE_MINIMUM, self.POINT_SIZE_MAXIMUM
        )
        settings["point_size"].setToolTip("Point size of the application.")

        # Set the default values
        controller = self.model.controller
        settings["host"].setText(controller.host)
        settings["port_command"].setValue(controller.port_command)
        settings["port_telemetry"].setValue(controller.port_telemetry)
        settings["timeout_connection"].setValue(controller.timeout_connection)
        settings["log_level"].setValue(self.model.log.level)

        # The unit of self.model.duration_refresh is milliseconds
        frequency = int(1000 / self.model.duration_refresh)
        settings["refresh_frequency"].setValue(frequency)

        app = QApplication.instance()
        settings["point_size"].setValue(app.font().pointSize())

        self._set_minimum_width_line_edit(settings["host"])

        return settings

    def _set_minimum_width_line_edit(self, line_edit, offset=20):
        """Set the minimum width of line edit.

        Parameters
        ----------
        line_edit : `PySide2.QtWidgets.QLineEdit`
            Line edit.
        offset : `int`, optional
            Offset of the width. (the default is 20)
        """

        font_metrics = line_edit.fontMetrics()

        text = line_edit.text()
        width = font_metrics.boundingRect(text).width()
        line_edit.setMinimumWidth(width + offset)

    @asyncSlot()
    async def _callback_apply_host(self):
        """Callback of the apply-host-setting button. This will apply the
        new host settings to model."""

        host = self._settings["host"].text()
        port_command = self._settings["port_command"].value()
        port_telemetry = self._settings["port_telemetry"].value()
        timeout_connection = self._settings["timeout_connection"].value()

        await run_command(
            self.model.update_connection_information,
            host,
            port_command,
            port_telemetry,
            timeout_connection,
        )

    @asyncSlot()
    async def _callback_apply_general(self):
        """Callback of the apply-general-setting button. This will apply the
        new general settings to model."""

        self.model.log.setLevel(self._settings["log_level"].value())

        # The unit of self.model.duration_refresh is milliseconds
        self.model.duration_refresh = int(
            1000 / self._settings["refresh_frequency"].value()
        )

        # Update the point size
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(self._settings["point_size"].value())
        app.setFont(font)

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        layout.addWidget(self._create_group_tcpip())
        layout.addWidget(self._button_apply_host)

        layout.addWidget(self._create_group_application())
        layout.addWidget(self._button_apply_general)

        return layout

    def _create_group_tcpip(self):
        """Create the group of TCP/IP connection.

        Returns
        -------
        `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Host name:", self._settings["host"])
        layout.addRow("Commmand port:", self._settings["port_command"])
        layout.addRow("Telemetry port:", self._settings["port_telemetry"])
        layout.addRow("Connection timeout:", self._settings["timeout_connection"])

        return create_group_box("Tcp/Ip Connection", layout)

    def _create_group_application(self):
        """Create the group of application.

        Returns
        -------
        `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Point size:", self._settings["point_size"])
        layout.addRow("Logging level:", self._settings["log_level"])
        layout.addRow("Refresh frequency:", self._settings["refresh_frequency"])

        return create_group_box("Application", layout)
