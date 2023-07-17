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
from lsst.ts.m2com import DigitalInput, PowerType
from lsst.ts.m2gui import (
    DisplacementSensorDirection,
    ForceErrorTangent,
    TemperatureGroup,
    UtilityMonitor,
)
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


@pytest.fixture
def utility_monitor() -> UtilityMonitor:
    return UtilityMonitor()


def test_get_forces_axial(utility_monitor: UtilityMonitor) -> None:
    forces = utility_monitor.get_forces_axial()
    assert id(forces) != id(utility_monitor.forces_axial)


def test_get_forces_tangent(utility_monitor: UtilityMonitor) -> None:
    forces = utility_monitor.get_forces_tangent()
    assert id(forces) != id(utility_monitor.forces_tangent)


def test_report_utility_status(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    signals = [
        utility_monitor.signal_utility.power_motor_calibrated,
        utility_monitor.signal_utility.power_communication_calibrated,
        utility_monitor.signal_utility.power_motor_raw,
        utility_monitor.signal_utility.power_communication_raw,
        utility_monitor.signal_utility.inclinometer_raw,
        utility_monitor.signal_utility.inclinometer_processed,
        utility_monitor.signal_utility.inclinometer_tma,
        utility_monitor.signal_utility.breaker_status,
        utility_monitor.signal_utility.temperatures,
        utility_monitor.signal_utility.displacements,
        utility_monitor.signal_utility.digital_status_input,
        utility_monitor.signal_utility.digital_status_output,
        utility_monitor.signal_detailed_force.hard_points,
        utility_monitor.signal_detailed_force.forces_axial,
        utility_monitor.signal_detailed_force.forces_tangent,
        utility_monitor.signal_detailed_force.force_error_tangent,
        utility_monitor.signal_position.position,
        utility_monitor.signal_position.position_ims,
        utility_monitor.signal_net_force_moment.net_force_total,
        utility_monitor.signal_net_force_moment.net_moment_total,
        utility_monitor.signal_net_force_moment.force_balance,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        utility_monitor.report_utility_status()


def test_update_power_calibrated(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # Moter

    # There is the update
    signal_motor = utility_monitor.signal_utility.power_motor_calibrated
    with qtbot.waitSignal(signal_motor, timeout=TIMEOUT):
        utility_monitor.update_power_calibrated(PowerType.Motor, 0.11, 0.27)

    assert utility_monitor.power_motor_calibrated["voltage"] == 0.1
    assert utility_monitor.power_motor_calibrated["current"] == 0.3

    # There should be no update
    with qtbot.assertNotEmitted(signal_motor, wait=TIMEOUT):
        utility_monitor.update_power_calibrated(PowerType.Motor, 0.12, 0.28)

    assert utility_monitor.power_motor_calibrated["voltage"] == 0.1
    assert utility_monitor.power_motor_calibrated["current"] == 0.3

    # Communication

    # There is the update
    signal_communication = utility_monitor.signal_utility.power_communication_calibrated
    with qtbot.waitSignal(signal_communication, timeout=TIMEOUT):
        utility_monitor.update_power_calibrated(PowerType.Communication, 0.21, 0.37)

    assert utility_monitor.power_communication_calibrated["voltage"] == 0.2
    assert utility_monitor.power_communication_calibrated["current"] == 0.4


def test_update_power_raw(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # Moter

    # There is the update
    signal_motor = utility_monitor.signal_utility.power_motor_raw
    with qtbot.waitSignal(signal_motor, timeout=TIMEOUT):
        utility_monitor.update_power_raw(PowerType.Motor, 0.11, 0.27)

    assert utility_monitor.power_motor_raw["voltage"] == 0.1
    assert utility_monitor.power_motor_raw["current"] == 0.3

    # Communication

    # There is the update
    signal_communication = utility_monitor.signal_utility.power_communication_raw
    with qtbot.waitSignal(signal_communication, timeout=TIMEOUT):
        utility_monitor.update_power_raw(PowerType.Communication, 0.21, 0.37)

    assert utility_monitor.power_communication_raw["voltage"] == 0.2
    assert utility_monitor.power_communication_raw["current"] == 0.4


def test_update_inclinometer_angle(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    # There is the update
    signals = [
        utility_monitor.signal_utility.inclinometer_raw,
        utility_monitor.signal_utility.inclinometer_processed,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        utility_monitor.update_inclinometer_angle(0.16, new_angle_processed=1.13)

    assert utility_monitor.inclinometer_angle == 0.2

    # There should be no update
    with qtbot.assertNotEmitted(
        utility_monitor.signal_utility.inclinometer_raw, wait=TIMEOUT
    ):
        utility_monitor.update_inclinometer_angle(0.203)

    assert utility_monitor.inclinometer_angle == 0.2


def test_update_inclinometer_angle_tma(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    # There is the update
    signal = utility_monitor.signal_utility.inclinometer_tma
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_inclinometer_angle(0.16, is_internal=False)

    assert utility_monitor.inclinometer_angle_tma == 0.2

    # There should be no update
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_inclinometer_angle(0.203, is_internal=False)

    assert utility_monitor.inclinometer_angle_tma == 0.2


def test_get_temperature_sensors(utility_monitor: UtilityMonitor) -> None:
    sensors_intake = utility_monitor.get_temperature_sensors(TemperatureGroup.Intake)
    assert sensors_intake == ["Intake-1", "Intake-2"]

    sensors_exhaust = utility_monitor.get_temperature_sensors(TemperatureGroup.Exhaust)
    assert sensors_exhaust == ["Exhaust-1", "Exhaust-2"]

    sensors_lg2 = utility_monitor.get_temperature_sensors(TemperatureGroup.LG2)
    assert sensors_lg2 == ["LG2-1", "LG2-2", "LG2-3", "LG2-4"]

    sensors_lg3 = utility_monitor.get_temperature_sensors(TemperatureGroup.LG3)
    assert sensors_lg3 == ["LG3-1", "LG3-2", "LG3-3", "LG3-4"]

    sensors_lg4 = utility_monitor.get_temperature_sensors(TemperatureGroup.LG4)
    assert sensors_lg4 == ["LG4-1", "LG4-2", "LG4-3", "LG4-4"]


def test_get_displacement_sensors(utility_monitor: UtilityMonitor) -> None:
    sensors_theta = utility_monitor.get_displacement_sensors(
        DisplacementSensorDirection.Theta
    )

    assert sensors_theta == [
        "A1-Theta_z",
        "A2-Theta_z",
        "A3-Theta_z",
        "A4-Theta_z",
        "A5-Theta_z",
        "A6-Theta_z",
    ]

    sensors_delta = utility_monitor.get_displacement_sensors(
        DisplacementSensorDirection.Delta
    )

    assert sensors_delta == [
        "A1-Delta_z",
        "A2-Delta_z",
        "A3-Delta_z",
        "A4-Delta_z",
        "A5-Delta_z",
        "A6-Delta_z",
    ]


def test_update_breaker(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    name = "J1-W9-1"
    with qtbot.waitSignal(
        utility_monitor.signal_utility.breaker_status, timeout=TIMEOUT
    ):
        utility_monitor.update_breaker(name, True)

    assert utility_monitor.breakers[name] is True


def test_reset_breakers(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # There should be no signal
    signal = utility_monitor.signal_utility.breaker_status
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.reset_breakers(PowerType.Motor)

    # There is the signal
    name = "J1-W9-1"
    utility_monitor.update_breaker(name, True)

    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.reset_breakers(PowerType.Motor)

    assert utility_monitor.breakers[name] is False


def test_get_breakers(utility_monitor: UtilityMonitor) -> None:
    assert len(utility_monitor.get_breakers(PowerType.Motor)) == 9
    assert len(utility_monitor.get_breakers(PowerType.Communication)) == 6


def test_update_temperature(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # There is the update
    temperatures_group = TemperatureGroup.LG2
    temperatures = [1.1, 2.2, 3.3, 4.4]
    signal = utility_monitor.signal_utility.temperatures
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_temperature(temperatures_group, temperatures)

    sensors = utility_monitor.get_temperature_sensors(temperatures_group)
    for sensor, temperature in zip(sensors, temperatures):
        assert utility_monitor.temperatures[sensor] == temperature

    # There should be no update
    temperatures_small_change = [temperature + 0.01 for temperature in temperatures]
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_temperature(
            temperatures_group, temperatures_small_change
        )

    for sensor, temperature in zip(sensors, temperatures):
        assert utility_monitor.temperatures[sensor] == temperature


def test_update_temperature_exception(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    with pytest.raises(ValueError):
        utility_monitor.update_temperature(TemperatureGroup.Intake, [1.1] * 3)


def test_update_displacements(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # There is the update
    direction = DisplacementSensorDirection.Theta
    displacements = [1.1, 2.2, 3.3, 4.4, 5.5, 6.6]
    signal = utility_monitor.signal_utility.displacements
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_displacements(direction, displacements)

    sensors = utility_monitor.get_displacement_sensors(direction)
    for sensor, displacement in zip(sensors, displacements):
        assert utility_monitor.displacements[sensor] == displacement

    # There should be no update
    displacements_small_change = [
        displacement + 0.0001 for displacement in displacements
    ]
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_displacements(direction, displacements_small_change)

    sensors = utility_monitor.get_displacement_sensors(direction)
    for sensor, displacement in zip(sensors, displacements):
        assert utility_monitor.displacements[sensor] == displacement


def test_update_digital_status_input(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    # There is an update
    signal = utility_monitor.signal_utility.digital_status_input
    new_status = 1
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_digital_status_input(new_status)

    assert utility_monitor.digital_status_input == new_status

    # There should be no signal
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_digital_status_input(new_status)


def test_process_digital_status_input(utility_monitor: UtilityMonitor) -> None:
    value = (
        DigitalInput.J1_W9_1_MotorPowerBreaker.value
        + DigitalInput.InterlockPowerRelay.value
    )

    value_update = utility_monitor._process_digital_status_input(value)

    assert value_update & DigitalInput.J1_W9_1_MotorPowerBreaker.value == 0
    assert value_update & DigitalInput.InterlockPowerRelay.value == 0

    assert (
        value_update & DigitalInput.J2_W10_3_MotorPowerBreaker.value
        == DigitalInput.J2_W10_3_MotorPowerBreaker.value
    )


def test_update_digital_status_output(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    # There is an update
    signal = utility_monitor.signal_utility.digital_status_output
    new_status = 1
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_digital_status_output(new_status)

    assert utility_monitor.digital_status_output == new_status

    # There should be no signal
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_digital_status_output(new_status)


def test_update_hard_points(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    axial = [1, 2, 3]
    tangent = [72, 73, 74]
    with qtbot.waitSignal(
        utility_monitor.signal_detailed_force.hard_points, timeout=TIMEOUT
    ):
        utility_monitor.update_hard_points(axial, tangent)

    assert utility_monitor.hard_points["axial"] == axial
    assert utility_monitor.hard_points["tangent"] == tangent


def test_update_hard_points_exception(utility_monitor: UtilityMonitor) -> None:
    with pytest.raises(ValueError):
        utility_monitor.update_hard_points([1], [2])


def test_update_forces_exception_axial(utility_monitor: UtilityMonitor) -> None:
    with pytest.raises(ValueError):
        utility_monitor.update_forces_axial(utility_monitor.forces_axial)


def test_update_forces_exception_tangent(utility_monitor: UtilityMonitor) -> None:
    with pytest.raises(ValueError):
        utility_monitor.update_forces_tangent(utility_monitor.forces_tangent)


def test_update_forces_axial(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # Current force is changed
    actuator_force = utility_monitor.get_forces_axial()
    actuator_force.f_cur[1] = 100

    signal = utility_monitor.signal_detailed_force.forces_axial
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_forces_axial(actuator_force)

    assert id(utility_monitor.forces_axial) == id(actuator_force)
    assert utility_monitor.forces_axial.f_cur == actuator_force.f_cur

    # Current position is changed
    actuator_force = utility_monitor.get_forces_axial()
    actuator_force.position_in_mm[1] = 100

    signal = utility_monitor.signal_detailed_force.forces_axial
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_forces_axial(actuator_force)

    assert utility_monitor.forces_axial.position_in_mm == actuator_force.position_in_mm


def test_update_forces_tangent(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    # Current force is changed
    actuator_force = utility_monitor.get_forces_tangent()
    actuator_force.f_cur[1] = 100

    signal = utility_monitor.signal_detailed_force.forces_tangent
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_forces_tangent(actuator_force)

    assert id(utility_monitor.forces_tangent) == id(actuator_force)
    assert utility_monitor.forces_tangent.f_cur == actuator_force.f_cur

    # Current position is changed
    actuator_force = utility_monitor.get_forces_tangent()
    actuator_force.position_in_mm[1] = 100

    signal = utility_monitor.signal_detailed_force.forces_tangent
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_forces_tangent(actuator_force)

    assert (
        utility_monitor.forces_tangent.position_in_mm == actuator_force.position_in_mm
    )


def test_update_force_error_tangent(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    # Tangent force error is changed
    force_error_tangent = ForceErrorTangent()
    force_error_tangent.error_force[1] = 1.24
    force_error_tangent.error_weight = 1

    signal = utility_monitor.signal_detailed_force.force_error_tangent
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_force_error_tangent(force_error_tangent)

    assert (
        utility_monitor.force_error_tangent.error_weight
        == force_error_tangent.error_weight
    )
    assert utility_monitor.force_error_tangent.error_force[1] == 1.2

    # There should be no change
    force_error_tangent.error_weight = 1.001
    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_force_error_tangent(force_error_tangent)

    # Tangent sum is changed
    force_error_tangent.error_sum = 2
    force_error_tangent.error_force[2] = 2.24
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_force_error_tangent(force_error_tangent)

    assert (
        utility_monitor.force_error_tangent.error_sum == force_error_tangent.error_sum
    )
    assert utility_monitor.force_error_tangent.error_force[2] == 2.2


def test_update_position(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    signal = utility_monitor.signal_position.position
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_position(0.1, 0.23, 0.62, 3, 1.03, 1.06, is_ims=False)

    assert utility_monitor.position == [0.1, 0.2, 0.6, 3, 1, 1.1]

    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_position(0.11, 0.23, 0.62, 3, 1.03, 1.06, is_ims=False)

    assert utility_monitor.position[0] == 0.1


def test_update_position_ims(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    signal = utility_monitor.signal_position.position_ims
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_position(0.1, 0.23, 0.62, 3, 1.03, 1.06, is_ims=True)

    assert utility_monitor.position_ims == [0.1, 0.2, 0.6, 3, 1, 1.1]

    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_position(0.11, 0.23, 0.62, 3, 1.03, 1.06, is_ims=True)

    assert utility_monitor.position_ims[0] == 0.1


def test_update_net_force_moment_total(
    qtbot: QtBot, utility_monitor: UtilityMonitor
) -> None:
    # Force
    signal = utility_monitor.signal_net_force_moment.net_force_total
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_net_force_moment_total(
            [0.11, -0.22, -0.33], is_force=True
        )

    assert utility_monitor.net_force_total == [0.1, -0.2, -0.3]

    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_net_force_moment_total(
            [0.111, -0.22, -0.33], is_force=True
        )

    assert utility_monitor.net_force_total == [0.1, -0.2, -0.3]

    # Moment
    signal = utility_monitor.signal_net_force_moment.net_moment_total
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_net_force_moment_total(
            [0.11, -0.22, -0.33], is_force=False
        )

    assert utility_monitor.net_moment_total == [0.1, -0.2, -0.3]

    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_net_force_moment_total(
            [0.111, -0.22, -0.33], is_force=False
        )

    assert utility_monitor.net_moment_total == [0.1, -0.2, -0.3]


def test_update_force_balance(qtbot: QtBot, utility_monitor: UtilityMonitor) -> None:
    signal = utility_monitor.signal_net_force_moment.force_balance
    with qtbot.waitSignal(signal, timeout=TIMEOUT):
        utility_monitor.update_force_balance([0.11, -0.22, -0.33, 0.44, 0.55, -0.66])

    assert utility_monitor.force_balance == [0.1, -0.2, -0.3, 0.4, 0.6, -0.7]

    with qtbot.assertNotEmitted(signal, wait=TIMEOUT):
        utility_monitor.update_force_balance([0.111, -0.22, -0.33, 0.44, 0.55, -0.66])

    assert utility_monitor.force_balance == [0.1, -0.2, -0.3, 0.4, 0.6, -0.7]
