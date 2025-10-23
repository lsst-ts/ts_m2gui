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

import pytest
from lsst.ts.m2gui.display import ItemActuator, ViewMirror
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> ViewMirror:
    widget = ViewMirror()
    widget.add_item_actuator(1, "alias", 0, 0.5)

    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_show_selected_actuator_force(widget: ViewMirror) -> None:
    text_force = widget.get_text_force()
    assert text_force.isVisible() is False

    select_actuator(widget)
    await widget._show_selected_actuator_force()

    assert text_force.isVisible() is True


def select_actuator(widget: ViewMirror) -> None:
    for item in widget.items():
        if isinstance(item, ItemActuator):
            item.setSelected(True)


def test_get_selected_actuator(widget: ViewMirror) -> None:
    assert widget.get_selected_actuator() is None

    select_actuator(widget)
    assert widget.get_selected_actuator().acutator_id == 1


def test_get_text_force(widget: ViewMirror) -> None:
    text_force = widget.get_text_force()
    assert text_force.toPlainText().startswith("Actuator Force:") is True


def test_add_item_actuator(widget: ViewMirror) -> None:
    # The actuator was added in the widget() by widget.add_item_actuator()
    assert len(widget.actuators) == 1


def test_show_alias(widget: ViewMirror) -> None:
    actuator = widget.actuators[0]

    widget.show_alias(False)
    assert actuator.label_id.toPlainText() == "1"

    widget.show_alias(True)
    assert actuator.label_id.toPlainText() == "alias"


def test_item_actuator(widget: ViewMirror) -> None:
    actuator = widget.actuators[0]

    assert actuator.rect().x() == (widget.SIZE_SCENE - widget.DIAMETER) // 2
    assert actuator.rect().y() == 344

    assert actuator.pen().width() == 1

    assert actuator.label_id.x() == widget.SIZE_SCENE // 2 - actuator.label_id.font().pointSize()
    assert actuator.label_id.y() == actuator.rect().y()


def test_item_actuator_update_magnitude_exception(widget: ViewMirror) -> None:
    actuator = widget.actuators[0]
    with pytest.raises(ValueError):
        actuator.update_magnitude(0, 1, 1)

    with pytest.raises(ValueError):
        actuator.update_magnitude(0, 1, -1)


def test_item_actuator_update_magnitude(widget: ViewMirror) -> None:
    actuator = widget.actuators[0]

    actuator.update_magnitude(0, -700, 700)
    assert actuator.brush().color().hue() == 150

    # Test the magnitude is out of range
    actuator.update_magnitude(750, -700, 700)
    assert actuator.brush().color().hue() == 60

    actuator.update_magnitude(-750, -700, 700)
    assert actuator.brush().color().hue() == 240
