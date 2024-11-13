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

__all__ = ["TabDefault"]

import types
import typing

from lsst.ts.guitool import TabTemplate
from PySide6.QtWidgets import QComboBox, QFormLayout

from ..enums import Ring
from ..model import Model


class TabDefault(TabTemplate):
    """Default table.

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
        super().__init__(title)

        self.model = model

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide6.QtWidgets.QFormLayout`
            Layout.
        """
        layout.addRow(" ", None)

    def create_combo_box_ring_selection(
        self, callback_current_index_changed: typing.Callable | None = None
    ) -> QComboBox:
        """Create the combo box of ring selection.

        Parameters
        ----------
        callback_current_index_changed : `func` or None, optional
            Callback of the currentIndexChanged signal of ring_selection. (the
            default is None)

        Returns
        -------
        ring_selection : `PySide6.QtWidgets.QComboBox`
            Ring selection.
        """

        ring_selection = QComboBox()
        for specific_ring in Ring:
            ring_selection.addItem(specific_ring.name + " Ring")

        # Index begins from 0 instead of 1 in QComboBox
        index_B_ring = Ring.B.value - 1
        ring_selection.setCurrentIndex(index_B_ring)

        if callback_current_index_changed is not None:
            ring_selection.currentIndexChanged.connect(callback_current_index_changed)

        return ring_selection

    async def __aexit__(
        self,
        type: typing.Type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """This is an overridden function to support the asynchronous context
        manager."""
        await self.model.controller.close_controller_and_mock_server()
