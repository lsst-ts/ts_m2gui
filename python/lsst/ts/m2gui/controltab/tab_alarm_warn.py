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

from collections import OrderedDict
from pathlib import Path

from lsst.ts.m2com import (
    DEFAULT_ENABLED_FAULTS_MASK,
    MINIMUM_ERROR_CODE,
    read_error_code_file,
)
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..enums import LocalMode
from ..model import Model
from ..signals import SignalError
from ..utils import (
    create_group_box,
    create_label,
    create_table,
    prompt_dialog_warning,
    run_command,
    set_button,
)
from ..widget import QMessageBoxAsync
from .tab_default import TabDefault
from .tab_limit_switch_status import TabLimitSwitchStatus


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

    # Colors used in the label's text
    COLOR_RED = Qt.red.name.decode()

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # List of the errors
        self._error_list: dict = dict()

        # Label of the summary faults status
        self._label_summary_faults_status = create_label(
            name=hex(0),
            tool_tip=(
                "Cell controller's summary faults status as a U64 integer.\n"
                "Each bit means a specific error code restricted to the \n"
                "enabled faults mask."
            ),
        )

        # Label of the enabled faults mask
        self._label_enabled_faults_mask = create_label(
            name=hex(0),
            tool_tip=(
                "Mask to identify the faults. Each bit value means the \n"
                "allowed error code. If this value is 0, all the errors \n"
                "will be bypassed."
            ),
        )

        # Label of the bypassed error code
        self._label_error_code_bypass = create_label(
            name="None",
            tool_tip=(
                "Bypassed error codes. If the value is not None,\n"
                "the system might break."
            ),
        )

        # Table of the errors
        self._table_error = self._create_table_error()

        # Text of the possible error cause
        self._text_error_cause = self._create_text_error_cause()

        # Tab of the limit switch status
        self._tab_limit_switch_status = TabLimitSwitchStatus(
            "Limit Switch Status", model
        )

        # Bypass the selected error codes
        self._button_bypass_selected_errors = set_button(
            "Bypass Selected Errors", self._callback_bypass_selected_errors
        )

        # Reset the enabled faults mask to default
        self._button_reset_mask = set_button(
            "Reset Enabled Faults Mask", self._callback_reset_mask
        )

        # Show the widget of the limit switch status
        self._button_limit_switch_status = set_button(
            "Show Limit Switch Status",
            self._tab_limit_switch_status.show,
        )

        # Reset all alarms and warnings
        self._button_reset = set_button("Reset All Items", self._callback_reset)

        # Enable the open-loop maximum limit
        self._button_enable_open_loop_max_limit = set_button(
            "Enable Open-Loop Max Limits", self._callback_enable_open_loop_max_limit
        )

        self.set_widget_and_layout()

        # Set the callback of signal
        self._set_signal_error(self.model.fault_manager.signal_error)

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

    def create_layout(self) -> QHBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_error_list = QVBoxLayout()
        layout_error_list.addWidget(self._table_error)
        layout_error_list.addWidget(self._text_error_cause)

        layout.addLayout(layout_error_list)

        # Second column
        layout_status = QVBoxLayout()
        layout_status.addWidget(self._create_group_error_status())
        layout_status.addWidget(self._button_limit_switch_status)
        layout_status.addWidget(self._button_reset)
        layout_status.addWidget(self._button_enable_open_loop_max_limit)

        layout.addLayout(layout_status)

        return layout

    def _create_group_error_status(self) -> QGroupBox:
        """Create the group of error status.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout_faults_status = QFormLayout()
        layout_faults_status.addRow(
            "Summary Faults Status:", self._label_summary_faults_status
        )
        layout_faults_status.addRow(
            "Enabled Faults Mask:", self._label_enabled_faults_mask
        )
        layout_faults_status.addRow(
            "Bypassed Error Codes:", self._label_error_code_bypass
        )

        layout = QVBoxLayout()
        layout.addLayout(layout_faults_status)
        layout.addWidget(self._button_bypass_selected_errors)
        layout.addWidget(self._button_reset_mask)

        return create_group_box("Error/Warning Information", layout)

    @asyncSlot()
    async def _callback_bypass_selected_errors(self) -> None:
        """Callback of the bypass button to bypass the selected error codes."""

        codes = self._get_selected_error_codes()
        dialog = self._create_dialog_bypass(codes)

        result = await dialog.show()
        if result == QMessageBoxAsync.Ok:
            is_diagnostic_mode = await self._is_diagnostic_mode()
            if is_diagnostic_mode:
                (
                    enabled_faults_mask,
                    bits,
                ) = self.model.controller.error_handler.calc_enabled_faults_mask(
                    codes, int(self._label_enabled_faults_mask.text(), base=16)
                )
                self.model.log.debug(f"Bypass the error bits: {bits}.")

                await run_command(
                    self.model.controller.set_enabled_faults_mask, enabled_faults_mask
                )

    def _get_selected_error_codes(self) -> set:
        """Get the selected error codes.

        Returns
        -------
        `set`
            Selected error codes.
        """
        items = self._table_error.selectedItems()

        error_codes = set()
        for item in items:
            if item.column() == 0:
                error_codes.add(int(item.text()))

        return error_codes

    def _create_dialog_bypass(self, codes: set) -> QMessageBoxAsync:
        """Create a dialog to let user bypass the error codes.

        Parameters
        ----------
        codes : `set`
            Error codes to bypass.
        """

        dialog = QMessageBoxAsync()
        dialog.setIcon(QMessageBoxAsync.Warning)
        dialog.setWindowTitle("Bypass Selected Codes")

        if len(codes) == 0:
            dialog.setText("Please select the error codes to bypass related errors.")

        elif self._label_error_code_bypass.text() != "None":
            dialog.setText("Please reset the enabled faults mask first.")

        else:
            dialog.setText(
                f"Are you sure to bypass the error codes: {codes}?\n"
                "This action might break the system."
            )
            dialog.addButton(QMessageBoxAsync.Ok)

        dialog.addButton(QMessageBoxAsync.Cancel)

        # Block the user to interact with other running widgets
        dialog.setModal(True)

        return dialog

    async def _is_diagnostic_mode(self) -> bool:
        """Local mode is the diagnostic mode or not.

        Returns
        -------
        `bool`
            True if the local mode is diagnostic. Otherwise, False.
        """
        allowed_mode = LocalMode.Diagnostic
        if self.model.local_mode == allowed_mode:
            return True
        else:
            await prompt_dialog_warning(
                "_is_diagnostic_mode()",
                f"Enabled faults mask can only be updated in {allowed_mode!r}.",
            )
            return False

    @asyncSlot()
    async def _callback_reset_mask(self) -> None:
        """Callback of the reset-mask button to reset the enabled faults
        mask."""
        is_diagnostic_mode = await self._is_diagnostic_mode()
        if is_diagnostic_mode:
            await run_command(self.model.controller.reset_enabled_faults_mask)

    @asyncSlot()
    async def _callback_reset(self) -> None:
        """Callback of the reset button to reset all alarms and warnings."""

        self._text_error_cause.clear()

        await run_command(self.model.reset_errors)

    @asyncSlot()
    async def _callback_enable_open_loop_max_limit(self) -> None:
        """Callback of the enable button to enable the maximum limit of
        open-loop control."""
        await run_command(self.model.controller.enable_open_loop_max_limit, True)

    def _set_signal_error(self, signal_error: SignalError) -> None:
        """Set the error signal with callback functions.

        Parameters
        ----------
        signal_error : `SignalError`
            Signal of the error.
        """

        signal_error.summary_faults_status.connect(
            self._callback_signal_summary_faults_status
        )
        signal_error.enabled_faults_mask.connect(
            self._callback_signal_enabled_faults_mask
        )
        signal_error.error_new.connect(self._callback_signal_error_new)
        signal_error.error_cleared.connect(self._callback_signal_error_cleared)

    @asyncSlot()
    async def _callback_signal_summary_faults_status(self, status: int) -> None:
        """Callback of the error signal for the summary faults status. It is a
        U64 integer and each bit value means different error code.

        Parameters
        ----------
        status : `int`
            Summary faults status.
        """
        self._label_summary_faults_status.setText(hex(status))

    @asyncSlot()
    async def _callback_signal_enabled_faults_mask(self, mask: int) -> None:
        """Callback of the error signal for the enabled faults mask. It is a
        U64 integer and each bit value means the allowed error code.

        Parameters
        ----------
        mask : `int`
            Enabled faults mask.
        """
        # Show the received enabled faults mask
        self._label_enabled_faults_mask.setText(hex(mask))

        # Show the bypassed error codes
        mask_diff = DEFAULT_ENABLED_FAULTS_MASK - mask

        codes = list()
        for idx, error_code in enumerate(
            self.model.controller.error_handler.list_code_total
        ):
            if (mask_diff & (2**idx)) and (error_code >= MINIMUM_ERROR_CODE):
                codes.append(error_code)

        if len(codes) == 0:
            self._label_error_code_bypass.setText("None")
        else:
            codes.sort()
            self._label_error_code_bypass.setText(
                f"<font color='{self.COLOR_RED}'>{codes}</font>"
            )

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
        error_list = read_error_code_file(filepath)
        for error_code in list(error_list.keys()):
            if int(error_code) < MINIMUM_ERROR_CODE:
                error_list.pop(error_code)

        # Sort the error list
        self._error_list = OrderedDict(sorted(error_list.items()))

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
