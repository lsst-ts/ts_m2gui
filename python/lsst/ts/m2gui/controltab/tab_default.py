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

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QComboBox, QDockWidget, QFormLayout, QScrollArea, QWidget

from ..enums import Ring
from ..model import Model


class TabDefault(QDockWidget):
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
        super().__init__()
        self.setWindowTitle(title)

        self.setWidget(QWidget())

        self.model = model

        # Turn off the docker widget specific features
        # Because the code reuse in this project is mainly based on the
        # composition instead of inheritance in QT logic, these dock widget
        # features bring more troubles than the benifits.
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

    def set_widget_scrollable(
        self, widget: QWidget, is_resizable: bool = False
    ) -> QScrollArea:
        """Set the widget to be scrollable.

        Parameters
        ----------
        widget : `PySide2.QtWidgets.QWidget`
            Widget.
        is_resizable : `bool`, optional
            Is resizable or not. (the default is False)

        Returns
        -------
        scroll_area : `PySide2.QtWidgets.QScrollArea`
            Scrollable area.
        """

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(is_resizable)

        return scroll_area

    def add_empty_row_to_form_layout(self, layout: QFormLayout) -> None:
        """Add the empty row to the form layout.

        Parameters
        ----------
        layout : `PySide2.QtWidgets.QFormLayout`
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
        ring_selection : `PySide2.QtWidgets.QComboBox`
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

    def create_and_start_timer(self, callback_time_out: typing.Callable) -> QTimer:
        """Create and start the timer.

        Parameters
        ----------
        callback_time_out : `func`
            Callback function to handle the timeout. You may want to let the
            "callback_time_out" call the
            self.check_duration_and_restart_timer() to monitor the duration and
            restart the timer when the duration is changed.

        Returns
        -------
        timer : `PySide2.QtCore.QTimer`
            Timer.
        """

        timer = QTimer(self)
        timer.timeout.connect(callback_time_out)
        timer.start(self.model.duration_refresh)

        return timer

    def check_duration_and_restart_timer(self, timer: QTimer) -> None:
        """Check the duration and restart the timer if the duration has been
        updated.

        Parameters
        ----------
        timer : `PySide2.QtCore.QTimer`
            Timer.
        """

        if timer.interval() != self.model.duration_refresh:
            timer.start(self.model.duration_refresh)

    async def __aenter__(self) -> QDockWidget:
        """This is an overridden function to support the asynchronous context
        manager."""
        return self

    async def __aexit__(
        self,
        type: typing.Type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """This is an overridden function to support the asynchronous context
        manager."""
        await self.model.controller.close_tasks()
