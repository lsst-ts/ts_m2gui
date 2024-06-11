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

__all__ = ["LayoutDefault"]

from PySide6.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from ..model import Model


class LayoutDefault(object):
    """Layout of the default panel.

    Parameters
    ----------
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    layout : `PySide6.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model: Model) -> None:
        self.model = model
        self.model.signal_control.is_control_updated.connect(
            self._callback_signal_control
        )

        self.layout = self._set_layout()

    @asyncSlot()
    async def _callback_signal_control(self, is_control_updated: bool) -> None:
        """Callback of the control signal.

        Parameters
        ----------
        is_control_updated : `bool`
            Control is updated or not.
        """
        raise NotImplementedError("Child class needs to realize this function.")

    def _set_layout(self) -> QVBoxLayout:
        """Set the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """
        raise NotImplementedError("Child class needs to realize this function.")
