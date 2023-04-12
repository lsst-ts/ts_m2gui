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

__all__ = ["QMessageBoxAsync"]

import asyncio

from PySide2.QtWidgets import QMessageBox

from . import connect_signal_to_future


class QMessageBoxAsync(QMessageBox):
    """QT message box in the asynchronous version."""

    def show(self) -> asyncio.Future:
        """This is an overridden function.

        Based on the QT documents, we should avoid the use of exec().

        See:
        1. https://github.com/CabbageDevelopment/qasync/issues/59
        2. https://doc.qt.io/qt-6/qwidget.html#show
        3. https://doc.qt.io/qt-6/qmessagebox.html#open
        4. https://doc.qt.io/qt-6/qdialog.html#exec

        Returns
        -------
        future : `asyncio.Future`
            Future instance that represents an eventual result of an
            asynchronous operation.
        """
        return connect_signal_to_future(self.finished, super().show)
