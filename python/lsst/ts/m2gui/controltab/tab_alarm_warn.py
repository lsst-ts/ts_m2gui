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

__all__ = ["TabAlarmWarn"]

import csv

from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import (
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPlainTextEdit,
)

from ..utils import set_button, get_rgb_from_hex, colors
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

    def __init__(self, title, model):
        super().__init__(title, model)

        # List of the errors
        self._error_list = dict()

        # Table of the errors
        self._table_error = self._set_table()

        # Text of the possible error cause
        self._text_error_cause = self._set_text_error_cause()

        # Reset all alarms and warnings
        self._button_reset = None

        # Enable the open-loop maximum limit
        self._button_enable_open_loop_max_limit = None

        # Internal layout
        self._layout = self._set_layout()

        self.widget.setLayout(self._layout)

        # Highlighted errors
        self._errors = set()

        self._set_signal_error(self.model.signal_error)

    def _set_table(self):
        """Set the table widget.

        Returns
        -------
        table : `PySide2.QtWidgets.QTableWidget`
            Table widget.
        """

        table = QTableWidget()

        header_text = ["Error Code", "Error Reported"]
        table.setColumnCount(len(header_text))
        table.setHorizontalHeaderLabels(header_text)

        header = table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        table.itemSelectionChanged.connect(self._callback_selection_changed)

        return table

    @Slot()
    def _callback_selection_changed(self):
        """Callback of the selection changed on table."""

        items = self._table_error.selectedItems()

        error_code = str(items[0].text())

        try:
            error_detail = self._error_list[error_code]
            self._text_error_cause.setPlainText(error_detail[4])
        except KeyError:
            pass

    def _set_text_error_cause(self):
        """Set the text of possible error cause.

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

    def _set_layout(self):
        """Set the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        self._button_reset = set_button("Reset All Items", self._callback_reset)
        self._button_enable_open_loop_max_limit = set_button(
            "Enable OL Max Limits", self._callback_enable_open_loop_max_limit
        )

        layout = QVBoxLayout()
        layout.addWidget(self._table_error)
        layout.addWidget(self._text_error_cause)
        layout.addWidget(self._button_reset)
        layout.addWidget(self._button_enable_open_loop_max_limit)

        return layout

    @Slot()
    def _callback_reset(self):
        """Callback of the reset button to reset all alarms and warnings."""

        self._text_error_cause.clear()

        self.model.reset_errors()

        self._deemphasize_errors(self._errors)
        self._errors = set()

    def _deemphasize_errors(self, error_codes):
        """Deemphasize errors.

        Parameters
        ----------
        error_codes : `set [int]`
            Error codes.
        """

        default_color = get_rgb_from_hex(colors["White"])
        for error_code in error_codes:
            items = self._table_error.findItems(str(error_code), Qt.MatchExactly)
            if len(items) != 0:
                item = items[0]
                item.setBackground(default_color)

    @Slot()
    def _callback_enable_open_loop_max_limit(self):
        """Callback of the enable button to enable the maximum limit of
        open-loop control."""
        self.model.enable_open_loop_max_limit()

    def _set_signal_error(self, signal_error):
        """Set the error signal with callback functions.

        Parameters
        ----------
        signal_error : `SignalError`
            Signal of the error.
        """

        signal_error.error_codes_new.connect(self._callback_signal_error_new)
        signal_error.error_codes_cleared.connect(self._callback_signal_error_cleared)

    @Slot()
    def _callback_signal_error_new(self, error_codes):
        """Callback of the error signal for the new errors.

        Parameters
        ----------
        error_codes : `list [int]`
            New error codes.
        """

        new_errors = set(error_codes).difference(self._errors)
        self._highlight_errors(new_errors)

        self._errors.update(new_errors)

    def _highlight_errors(self, error_codes):
        """highlight the errors.

        Parameters
        ----------
        error_codes : `set [int]`
            Error codes.
        """

        for error_code in error_codes:
            items = self._table_error.findItems(str(error_code), Qt.MatchExactly)
            if len(items) != 0:
                error_detail = self._error_list[str(error_code)]
                status = error_detail[1].strip()
                self._set_error_item_color(items[0], status)

    def _set_error_item_color(self, item, status):
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
            item.setBackground(get_rgb_from_hex(colors["Red"]))
        elif status == "Warning":
            item.setBackground(get_rgb_from_hex(colors["Yellow"]))
        else:
            raise ValueError(f"Unsupported status: {status} to highlight the error.")

    @Slot()
    def _callback_signal_error_cleared(self, error_codes):
        """Callback of the error signal for the cleared errors.

        Parameters
        ----------
        error_codes : `list [int]`
            Cleared error codes.
        """

        cleared_errors = self._errors.intersection(error_codes)
        self._deemphasize_errors(cleared_errors)

        self._errors.difference_update(cleared_errors)

    def read_error_list_file(self, filepath):
        """Read the tsv file of error list.

        Parameters
        ----------
        filepath : `str` or `pathlib.PosixPath`
            File path.
        """

        self._error_list = dict()
        with open(filepath, "r") as file:
            csv_reader = csv.reader(file, delimiter="\t")

            # Skip the header
            next(csv_reader)

            # Get the error details
            for row in csv_reader:
                self._error_list[row[0]] = row[1:]

        self._add_error_list_to_table()
        self._resize_table_error()

    def _add_error_list_to_table(self):
        """Add the error list to table."""

        self._table_error.setRowCount(len(self._error_list))

        for idx, (code, detail) in enumerate(self._error_list.items()):
            item_code = QTableWidgetItem(code)
            item_error_reported = QTableWidgetItem(detail[0])
            self._table_error.setItem(idx, 0, item_code)
            self._table_error.setItem(idx, 1, item_error_reported)

    def _resize_table_error(self, margin=50):
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
