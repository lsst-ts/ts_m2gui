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

__all__ = ["TabRealtimeNetForceMoment"]

from lsst.ts.guitool import FigureConstant
from PySide6.QtWidgets import QGridLayout
from qasync import asyncSlot

from ..model import Model
from .tab_default import TabDefault


class TabRealtimeNetForceMoment(TabDefault):
    """Table of the realtime net force and moment.

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
    net_force_moment : `list`
        Data of the net force and moment: [fx, fy, fz, mx, my, mz]. The unit of
        force is Newton and the unit of moment is Newton * meter.
    """

    MIN_WIDTH = 150

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        self.net_force_moment = [0.0] * 6

        # Realtime figures
        self._figures = self._create_figures()

        # Timer to update the realtime figures
        self._timer = self.create_and_start_timer(self._callback_time_out)

        self.set_widget_and_layout()

    def _create_figures(self, num_realtime: int = 200) -> dict:
        """Create the figures to show the net force and moment.

        Parameters
        ----------
        num_realtime : `int`, optional
            Number of the realtime data (>=0). (the default is 200)

        Returns
        -------
        figures : `dict`
            Figures of the net force and moment.
        """

        figures = dict()
        axes = ["fx", "fy", "fz", "mx", "my", "mz"]
        for axis in axes:
            label_y = "Force (N)" if axis.startswith("f") else "Moment (N m)"
            figures[axis] = FigureConstant(
                1,
                num_realtime,
                num_realtime,
                "Data Point",
                label_y,
                axis,
                legends=[],
                num_lines=1,
                is_realtime=True,
            )

        for figure in figures.values():
            figure.axis_x.setLabelFormat("%d")

        return figures

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to update the realtime figures."""

        for idx, figure in enumerate(self._figures.values()):
            figure.append_data(self.net_force_moment[idx])

        self.check_duration_and_restart_timer(self._timer)

    def create_layout(self) -> QGridLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QGridLayout`
            Layout.
        """

        layout = QGridLayout()

        # Only draw the data with two rows
        axes = self._figures.keys()
        max_column = round(len(axes) / 2)

        for index, axis in enumerate(axes):
            figure = self._figures[axis]
            figure.setMinimumWidth(self.MIN_WIDTH)

            row, column = divmod(index, max_column)
            layout.addWidget(figure, row, column)

        return layout
