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

__all__ = ["QFileDialogAsync"]

import sys

from PySide2.QtWidgets import QFileDialog

from . import connect_signal_to_future


class QFileDialogAsync(QFileDialog):
    """QT file dialog in the asynchronous version."""

    async def get_open_filename_async(self):
        """Get the existed file selected by the user.

        Returns
        -------
        `str`
            Selected file. If the user presses 'Cancel', it returns an empty
            string.
        """

        # Block the user to interact with other running widgets
        self.setModal(True)

        # Fix linux crash if not native QFileDialog is async
        if sys.platform != "linux":
            self.setOption(QFileDialog.DontUseNativeDialog, True)

        self.setAcceptMode(QFileDialog.AcceptOpen)

        result = await self.show()

        if result == QFileDialog.AcceptSave:
            return self.selectedFiles()[0]
        else:
            return ""

    def show(self):
        """This is an overridden function.

        See QMessageBoxAsync.show() for the details.

        Returns
        -------
        future : `asyncio.Future`
            Future instance that represents an eventual result of an
            asynchronous operation.
        """
        return connect_signal_to_future(self.finished, super().show)
