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

__all__ = ["ControlTabs"]

from PySide2.QtWidgets import QListWidget, QVBoxLayout
from PySide2.QtCore import Slot, Qt

from .utils import set_button
from .controltab import (
    TabActuatorControl,
    TabAlarmWarn,
    TabCellStatus,
    TabConfigView,
    TabDetailedForce,
    TabDiagnostics,
    TabOverview,
    TabRigidBodyPos,
    TabUtilityView,
)


class ControlTabs(object):
    """Control tables.

    Attributes
    ----------
    layout : `PySide2.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self):

        # Show the selected table or not
        self._button_show = None

        # List of the control tables
        self._tabs = list()

        # Widget to have the list of control tables
        self._list_widget = QListWidget()

        self._setup_tabs_and_list_widget()

        self.layout = self._set_layout()

        # Set the default selection
        self._list_widget.setCurrentItem(self.get_tab("Overview")[0])

    def _setup_tabs_and_list_widget(self):
        """Setup the tables and list widget."""

        self._tabs = [
            TabOverview("Overview"),
            TabActuatorControl("Actuator Control"),
            TabConfigView("Configuration View"),
            TabCellStatus("Cell Status"),
            TabUtilityView("Utility View"),
            TabRigidBodyPos("Rigid Body Position"),
            TabDetailedForce("Detailed Force"),
            TabDiagnostics("Diagnostics"),
            TabAlarmWarn("Alarms/Warnings"),
        ]

        for tab in self._tabs:
            self._list_widget.addItem(tab.windowTitle())

    def _set_layout(self):
        """Set the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """
        self._button_show = set_button("Show Selected Table", self._callback_show)

        layout = QVBoxLayout()
        layout.addWidget(self._list_widget)
        layout.addWidget(self._button_show)

        return layout

    @Slot()
    def _callback_show(self):
        """Callback of the show button."""
        item = self._list_widget.currentItem()
        control_tab = self._get_control_tab(item.text())
        control_tab.show()

    def get_tab(self, name):
        """Get the table.

        Parameters
        ----------
        name : `str`
            Name of the Table.

        Returns
        -------
        item : `PySide2.QtWidgets.QListWidgetItem` or None
            Table item object. None if nothing.
        control_tab : Child of `TabDefault` or None
            Control table object. None if nothing.
        """

        try:
            item = self._list_widget.findItems(name, Qt.MatchExactly)[0]
            control_tab = self._get_control_tab(name)
            return item, control_tab

        except IndexError:
            return None, None

    def _get_control_tab(self, title):
        """Get the control table.

        Parameters
        ----------
        title : `str`
            Title of the control table.

        Returns
        -------
        Child of `TabDefault` or None
            Control table object. None if nothing.
        """
        for tab in self._tabs:
            if tab.windowTitle() == title:
                return tab

        return None
