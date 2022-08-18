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

__all__ = ["TabSettings"]

from qasync import asyncSlot

from PySide2.QtWidgets import QVBoxLayout, QFormLayout, QLineEdit, QSpinBox

from ..utils import set_button, create_group_box, run_command
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

    TIMEOUT_MINIMUM = 1

    def __init__(self, title, model):
        super().__init__(title, model)

        self._settings = self._create_settings()

        self._button_apply = set_button("Apply Settings", self._callback_apply)

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
        }

        for port in ("port_command", "port_telemetry"):
            settings[port].setRange(self.PORT_MINIMUM, self.PORT_MAXIMUM)

        settings["timeout_connection"].setMinimum(self.TIMEOUT_MINIMUM)
        settings["timeout_connection"].setSuffix(" sec")

        # Set the default values
        settings["host"].setText(self.model.host)
        settings["port_command"].setValue(self.model.port_command)
        settings["port_telemetry"].setValue(self.model.port_telemetry)
        settings["timeout_connection"].setValue(self.model.timeout_connection)

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
    async def _callback_apply(self):
        """Callback of the apply button. This will apply the settings."""

        host = self._settings["host"].text()
        port_command = self._settings["port_command"].value()
        port_telemetry = self._settings["port_telemetry"].value()
        timeout_connection = self._settings["timeout_connection"].value()

        run_command(
            self.model.update_connection_information,
            host,
            port_command,
            port_telemetry,
            timeout_connection,
        )

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        layout.addWidget(self._create_group_tcpip())
        layout.addWidget(self._button_apply)

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
