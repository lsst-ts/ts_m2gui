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

__all__ = ["TabAlarmWarn"]

from pathlib import Path

from lsst.ts.m2com import LimitSwitchType, read_error_code_file
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..enums import Ring, Status
from ..model import Model
from ..signals import SignalError, SignalLimitSwitch
from ..utils import create_label, create_table, run_command, set_button
from . import TabDefault


class TabAlarmWarn(TabDefault):
    """Table of the alarms and warnings.

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

        # List of the errors
        self._error_list: dict = dict()

        # Table of the errors
        self._table_error = self._create_table_error()

        # Text of the possible error cause
        self._text_error_cause = self._create_text_error_cause()

        # Indicators of the limit switch
        self._indicators_limit_switch_retract = self._create_indicators_limit_switch(
            LimitSwitchType.Retract
        )
        self._indicators_limit_switch_extend = self._create_indicators_limit_switch(
            LimitSwitchType.Extend
        )

        # Reset all alarms and warnings
        self._button_reset = None

        # Enable the open-loop maximum limit
        self._button_enable_open_loop_max_limit = None

        # Internal layout
        self.widget().setLayout(self._create_layout())

        # Resize the dock to have a similar size of layout
        self.resize(self.widget().sizeHint())

        # Set the callbacks of signals
        self._set_signal_error(self.model.fault_manager.signal_error)
        self._set_signal_limit_switch(self.model.fault_manager.signal_limit_switch)

    def _create_table_error(self) -> QTableWidget:
        """Create the table widget of error code.

        Returns
        -------
        table : `PySide2.QtWidgets.QTableWidget`
            Table widget.
        """

        header_text = ["Error Code", "Error Reported"]
        table = create_table(header_text)

        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        table.itemSelectionChanged.connect(self._callback_selection_changed)

        return table

    @asyncSlot()
    async def _callback_selection_changed(self) -> None:
        """Callback of the selection changed on table."""

        items = self._table_error.selectedItems()

        try:
            error_code = str(items[0].text())
            error_detail = self._error_list[error_code]
            self._text_error_cause.setPlainText(error_detail[4])
        except (KeyError, IndexError):
            pass

    def _create_text_error_cause(self) -> QPlainTextEdit:
        """Create the text of possible error cause.

        Returns
        -------
        text_error_cause : `PySide2.QtWidgets.QPlainTextEdit`
            Text of the possible error cause.
        """

        text_error_cause = QPlainTextEdit()
        text_error_cause.setPlaceholderText("Possible Error Cause")
        text_error_cause.setReadOnly(True)

        n_rows = 3
        font_metrics = text_error_cause.fontMetrics()
        text_error_cause.setMaximumHeight(n_rows * font_metrics.lineSpacing())

        return text_error_cause

    def _create_indicators_limit_switch(
        self, limit_switch_type: LimitSwitchType
    ) -> dict[str, QPushButton]:
        """Creates indicators for limit switches.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.

        Returns
        -------
        indicators : `dict`
            Indicators of limit switch.

        Raises
        ------
        ValueError
            Unsupported limit switch type.
        """

        if limit_switch_type == LimitSwitchType.Retract:
            limit_switch_status = self.model.fault_manager.limit_switch_status_retract
        elif limit_switch_type == LimitSwitchType.Extend:
            limit_switch_status = self.model.fault_manager.limit_switch_status_extend
        else:
            raise ValueError(f"Unsupported limit switch type: {limit_switch_type!r}.")

        indicators = dict()
        for name in limit_switch_status.keys():
            indicator = set_button(
                name,
                None,
                is_indicator=True,
                is_adjust_size=True,
                tool_tip="Green: Normal\nYellow: Software limit\nRed: Triggered",
            )

            self._update_indicator_color(indicator, Status.Normal)

            indicators[name] = indicator

        return indicators

    def _update_indicator_color(self, indicator: QPushButton, status: Status) -> None:
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide2.QtWidgets.QPushButton`
            Indicator.
        status : enum `Status`
            Status.
        """

        palette = indicator.palette()

        if status == Status.Normal:
            palette.setColor(QPalette.Button, Qt.green)
        elif status == Status.Alert:
            palette.setColor(QPalette.Button, Qt.yellow)
        else:
            palette.setColor(QPalette.Button, Qt.red)

        indicator.setPalette(palette)

    def _create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        self._button_reset = set_button("Reset All Items", self._callback_reset)
        self._button_enable_open_loop_max_limit = set_button(
            "Enable Open-Loop Max Limits", self._callback_enable_open_loop_max_limit
        )

        layout = QVBoxLayout()
        layout.addWidget(self._table_error)
        layout.addWidget(self._text_error_cause)
        layout.addWidget(create_label(name="Limit Switch Status", is_bold=True))
        layout.addWidget(self._get_widget_limit_switch())
        layout.addWidget(self._button_reset)
        layout.addWidget(self._button_enable_open_loop_max_limit)

        return layout

    def _get_widget_limit_switch(self) -> QScrollArea:
        """Get the widget of limit switch.

        Returns
        -------
        scroll_area : `PySide2.QtWidgets.QScrollArea`
            Widget of limit switch.
        """

        widget = QWidget()

        layout = QHBoxLayout(widget)
        for ring in (Ring.B, Ring.C, Ring.D, Ring.A):
            layout.addLayout(
                self._get_layout_limit_switch_specific_ring(
                    LimitSwitchType.Retract, ring
                )
            )
            layout.addLayout(
                self._get_layout_limit_switch_specific_ring(
                    LimitSwitchType.Extend, ring
                )
            )

        return self.set_widget_scrollable(widget)

    def _get_layout_limit_switch_specific_ring(
        self, limit_switch_type: LimitSwitchType, ring: Ring
    ) -> QVBoxLayout:
        """Get the layout of limit switch in specific ring.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.
        ring : enum `Ring`
            Name of ring.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout of limit switch.
        """

        if limit_switch_type == LimitSwitchType.Retract:
            indicators = self._indicators_limit_switch_retract
            label = create_label(name="Retract")
        elif limit_switch_type == LimitSwitchType.Extend:
            indicators = self._indicators_limit_switch_extend
            label = create_label(name="Extend")
        else:
            raise ValueError(f"Unsupported limit switch type: {limit_switch_type!r}.")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(label)
        for name, indicator in indicators.items():
            if name.startswith(ring.name):
                layout.addWidget(indicator)

        return layout

    @asyncSlot()
    async def _callback_reset(self) -> None:
        """Callback of the reset button to reset all alarms and warnings."""

        self._text_error_cause.clear()

        await run_command(self.model.reset_errors)

    @asyncSlot()
    async def _callback_enable_open_loop_max_limit(self) -> None:
        """Callback of the enable button to enable the maximum limit of
        open-loop control."""
        await run_command(self.model.enable_open_loop_max_limit, True)

    def _set_signal_error(self, signal_error: SignalError) -> None:
        """Set the error signal with callback functions.

        Parameters
        ----------
        signal_error : `SignalError`
            Signal of the error.
        """

        signal_error.error_new.connect(self._callback_signal_error_new)
        signal_error.error_cleared.connect(self._callback_signal_error_cleared)

    @asyncSlot()
    async def _callback_signal_error_new(self, error_code: int) -> None:
        """Callback of the error signal for the new error. This function will
        highlight the error.

        Parameters
        ----------
        error_code : `int`
            New error code.
        """

        items = self._table_error.findItems(str(error_code), Qt.MatchExactly)
        if len(items) != 0:
            error_detail = self._error_list[str(error_code)]
            status = error_detail[1].strip()
            self._set_error_item_color(items[0], status)

    def _set_error_item_color(self, item: QTableWidgetItem, status: str) -> None:
        """Set the error/warning item with specific color.

        Parameters
        ----------
        item : `PySide2.QtWidgets.QTableWidgetItem`
            Table widget item.
        status : `str`
            Error status.

        Raises
        ------
        ValueError
            Unsupported status to highlight the error.
        """

        if status == "Fault":
            item.setBackground(Qt.red)
        elif status == "Warning":
            item.setBackground(Qt.yellow)
        else:
            raise ValueError(f"Unsupported status: {status} to highlight the error.")

    @asyncSlot()
    async def _callback_signal_error_cleared(self, error_code: int) -> None:
        """Callback of the error signal for the cleared error. This function
        will deemphasize the error.

        Parameters
        ----------
        error_code : `int`
            Cleared error code.
        """

        items = self._table_error.findItems(str(error_code), Qt.MatchExactly)
        if len(items) != 0:
            item = items[0]
            item.setBackground(Qt.white)

    def _set_signal_limit_switch(self, signal_limit_switch: SignalLimitSwitch) -> None:
        """Set the limit switch signal with callback function.

        Parameters
        ----------
        signal_limit_switch : `SignalLimitSwitch`
            Signal of the limit switch.
        """

        signal_limit_switch.type_name_status.connect(self._callback_signal_limit_switch)

    @asyncSlot()
    async def _callback_signal_limit_switch(self, type_name_status: tuple) -> None:
        """Callback of the limit switch signal.

        Parameters
        ----------
        type_name_status : `tuple`
            A tuple: (type, name, status). The data type of type is integer
            (enum `lsst.ts.m2com.LimitSwitchType`), the data type of name is
            string, and the data type of status is integer (enum `Status`).
        """

        limit_switch_type = LimitSwitchType(type_name_status[0])
        if limit_switch_type == LimitSwitchType.Retract:
            indicators = self._indicators_limit_switch_retract
        elif limit_switch_type == LimitSwitchType.Extend:
            indicators = self._indicators_limit_switch_extend

        name = type_name_status[1]

        self._update_indicator_color(indicators[name], Status(type_name_status[2]))

    def read_error_list_file(self, filepath: str | Path) -> None:
        """Read the tsv file of error list.

        Parameters
        ----------
        filepath : `str` or `pathlib.PosixPath`
            File path.
        """

        # Randomly-chosen minimum error code by vendor
        MINIMUM_ERROR_CODE = 6000

        # Read the file and pop out the dummy error code
        self._error_list = read_error_code_file(filepath)
        for error_code in list(self._error_list.keys()):
            if int(error_code) < MINIMUM_ERROR_CODE:
                self._error_list.pop(error_code)

        self._add_error_list_to_table()
        self._resize_table_error()

    def _add_error_list_to_table(self) -> None:
        """Add the error list to table."""

        self._table_error.setRowCount(len(self._error_list))

        for idx, (code, detail) in enumerate(self._error_list.items()):
            item_code = QTableWidgetItem(code)
            item_error_reported = QTableWidgetItem(detail[0])
            self._table_error.setItem(idx, 0, item_code)
            self._table_error.setItem(idx, 1, item_error_reported)

    def _resize_table_error(self, margin: int = 50) -> None:
        """Resize the table of error list.

        Parameters
        ----------
        margin : `int`, optional
            Margin of table in pixel. (the default is 50)
        """

        header_horizontal = self._table_error.horizontalHeader()
        header_vertical = self._table_error.verticalHeader()

        total_width = header_vertical.width()
        for idx in range(self._table_error.columnCount()):
            total_width += header_horizontal.sectionSize(idx)

        self._table_error.setMinimumWidth(total_width + margin)
