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

__all__ = ["Model"]

import logging

from .enums import LocalMode


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger` or None, optional
        A logger. If None, a logger will be instantiated. (the default is
        None)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    is_csc_commander : `bool`
        Commandable SAL component (CSC) is the commander or not.
    local_mode : `LocalMode`
        Local model.
    is_closed_loop : `bool`
        Closed-loop control is on or not.
    """

    def __init__(self, log=None):

        # Set the logger
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        self.is_csc_commander = False
        self.local_mode = LocalMode.Standby
        self.is_closed_loop = False
