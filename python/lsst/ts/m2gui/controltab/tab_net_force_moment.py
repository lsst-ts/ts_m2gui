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

__all__ = ["TabNetForceMoment"]

from PySide2.QtWidgets import QFormLayout, QGroupBox, QVBoxLayout

from ..model import Model
from ..signals import SignalNetForceMoment
from ..utils import create_group_box, create_label, set_button
from .tab_default import TabDefault
from .tab_realtime_net_force_moment import TabRealtimeNetForceMoment


class TabNetForceMoment(TabDefault):
    """Table of the net force and moment.

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

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # Collection of the labels of total actuator net force and moment
        self._net_force_moment_total = {
            "fx": create_label(tool_tip="Total actuator net x-force."),
            "fy": create_label(tool_tip="Total actuator net y-force."),
            "fz": create_label(tool_tip="Total actuator net z-force."),
            "mx": create_label(tool_tip="Total actuator net x-moment."),
            "my": create_label(tool_tip="Total actuator net y-moment."),
            "mz": create_label(tool_tip="Total actuator net z-moment."),
        }

        # Collection of the labels of force balance status
        self._force_balance = {
            "fx": create_label(tool_tip="X-force based on hardpoint correction."),
            "fy": create_label(tool_tip="Y-force based on hardpoint correction."),
            "fz": create_label(tool_tip="Z-force based on hardpoint correction."),
            "mx": create_label(tool_tip="X-moment based on hardpoint correction."),
            "my": create_label(tool_tip="Y-moment based on hardpoint correction."),
            "mz": create_label(tool_tip="Z-moment based on hardpoint correction."),
        }

        # Tables to show the realtime data
        self._tab_realtime_net_force_moment_total = TabRealtimeNetForceMoment(
            "Total Actuator Status", model
        )
        self._tab_realtime_force_balance = TabRealtimeNetForceMoment(
            "Force Balance Status", model
        )

        # Buttons to show the realtime data
        self._button_realtime_net_force_moment_total = set_button(
            "Show Realtime Data",
            self._tab_realtime_net_force_moment_total.show,
        )
        self._button_realtime_force_balance = set_button(
            "Show Realtime Data",
            self._tab_realtime_force_balance.show,
        )

        self._set_widget_and_layout()

        self._set_signal_net_force_moment(
            self.model.utility_monitor.signal_net_force_moment
        )

    def _set_widget_and_layout(self) -> None:
        """Set the widget and layout."""

        widget = self.widget()
        widget.setLayout(self._create_layout())

        # Resize the dock to have a similar size of layout
        self.resize(widget.sizeHint())

    def _create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        layout.addWidget(self._create_group_net_force_moment_total())
        layout.addWidget(self._create_group_force_balance())

        return layout

    def _create_group_net_force_moment_total(self) -> QGroupBox:
        """Create the group of total net force and moment.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_data = QFormLayout()
        for axis in self._net_force_moment_total.keys():
            layout_data.addRow(f"{axis}:", self._net_force_moment_total[axis])

        layout.addLayout(layout_data)
        layout.addWidget(self._button_realtime_net_force_moment_total)

        return create_group_box("Total Net Force and Moment", layout)

    def _create_group_force_balance(self) -> QGroupBox:
        """Create the group of force balance status.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_data = QFormLayout()
        for axis in self._force_balance.keys():
            layout_data.addRow(f"{axis}:", self._force_balance[axis])

        layout.addLayout(layout_data)
        layout.addWidget(self._button_realtime_force_balance)

        return create_group_box("Force Balance Status", layout)

    def _set_signal_net_force_moment(
        self,
        signal_net_force_moment: SignalNetForceMoment,
    ) -> None:
        """Set the net force/moment signal with callback functions. This signal
        provides the details of total actuator net force and moment, and force
        balance status.

        Parameters
        ----------
        signal_net_force_moment : `SignalNetForceMoment`
            Signal of the net force and moment.
        """

        signal_net_force_moment.net_force_total.connect(
            self._callback_signal_net_force_total
        )
        signal_net_force_moment.net_moment_total.connect(
            self._callback_signal_net_moment_total
        )

        signal_net_force_moment.force_balance.connect(
            self._callback_signal_force_balance
        )

    def _callback_signal_net_force_total(self, net_force_total: list[float]) -> None:
        """Callback of the net force/moment signal for the new total net force.

        Parameters
        ----------
        net_force_total : `list`
            Total actuator net force in Newton as [fx, fy, fz] for x, y, and z
            dimensions.
        """

        net_force_moment = self._tab_realtime_net_force_moment_total.net_force_moment

        axes = ["fx", "fy", "fz"]
        for idx, axis in enumerate(axes):
            net_force_moment[idx] = net_force_total[idx]

            self._net_force_moment_total[axis].setText(f"{net_force_total[idx]} N")

    def _callback_signal_net_moment_total(self, net_moment_total: list[float]) -> None:
        """Callback of the net force/moment signal for the new total net
        moment.

        Parameters
        ----------
        net_moment_total : `list`
            Total actuator net moment in Newton * meter as [mx, my, mz] for x,
            y, and z dimensions.
        """

        net_force_moment = self._tab_realtime_net_force_moment_total.net_force_moment

        axes = ["mx", "my", "mz"]
        for idx, axis in enumerate(axes):
            net_force_moment[idx + 3] = net_moment_total[idx]

            self._net_force_moment_total[axis].setText(f"{net_moment_total[idx]} N * m")

    def _callback_signal_force_balance(self, force_balance: list[float]) -> None:
        """Callback of the net force/moment signal for the new force balance
        status.

        Parameters
        ----------
        force_balance : `list`
            Force balance status as [fx, fy, fz, mx, my, mz] based on the
            hardpoint correction for x, y, and z dimensions. The units of force
            and moment are Newton and Newton * meter.
        """

        net_force_moment = self._tab_realtime_force_balance.net_force_moment

        for idx, axis in enumerate(self._force_balance.keys()):
            net_force_moment[idx] = force_balance[idx]

            unit = "N" if (idx < 3) else "N * m"
            self._force_balance[axis].setText(f"{force_balance[idx]} {unit}")
