.. py:currentmodule:: lsst.ts.m2gui

.. _lsst.ts.m2gui-version_history:

##################
Version History
##################

.. _lsst.ts.m2gui-0.6.0:

-------------
0.6.0
-------------

* Migrate the functions to **ts_m2com**

.. _lsst.ts.m2gui-0.5.1:

-------------
0.5.1
-------------

* Add the **tab_net_force_moment.py** and **tab_realtime_net_force_moment.py**.
* Add the new signal: **SignalNetForceMoment**.
* Update the ``FigureConstant.append_data()`` to regularly check the y-axis needs to be adjusted or not.

.. _lsst.ts.m2gui-0.5.0:

-------------
0.5.0
-------------

* Use the migrated functions in **Controller** class in **ts_m2com**.
* Add the control parameters and look-up table (LUT) parameters in the tab of settings.
* Subscribe the event: **temperatureOffset**.

.. _lsst.ts.m2gui-0.4.7:

-------------
0.4.7
-------------

* Add the classes of ``ActuatorForceAxial`` and ``ActuatorForceTangent`` to replace the ``ActuatorForce`` class to minimize the duplication.

.. _lsst.ts.m2gui-0.4.6:

-------------
0.4.6
-------------

* Subscribe the event of available configuration files from the controller.
* Allow the user to select the configuration file to set in the controller.

.. _lsst.ts.m2gui-0.4.5:

-------------
0.4.5
-------------

* Show the summary faults status and enabled faults mask.
* Allow the user to set the enabled faults mask.

.. _lsst.ts.m2gui-0.4.4:

-------------
0.4.4
-------------

* Sort the error list in ``TabAlarmWarn`` class.
* Update the ``TabDiagnostics._callback_force_error_tangent()`` to let the text's color is based on the threshold.

.. _lsst.ts.m2gui-0.4.3:

-------------
0.4.3
-------------

* Rename the "isInterlockOn" with "isInterlockEnabled" to be consistent with the controller.
The indicator's color should be green instead of red when the status is on.
* Simplify the ``UtilityMonitor.update_forces()`` to remove the check of force change.
* Update the ``Model.connect()`` to actively clear the error if any when the connection is constructed.
* Update the ``UtilityMonitor.update_position()`` to publish the position by IMS.
* Add the ``TabRigidBodyPos._create_group_ims_position()`` to show the position by IMS.
* Change the digit in detailed force widget.
* Update the condition to trigger the ``Model.fault()``.
* Update the ``Model._process_telemetry()`` to deal with the condition that the hardpoint correction of tangent link might be empty.

.. _lsst.ts.m2gui-0.4.2:

-------------
0.4.2
-------------

* Support the bit status in ``Model.set_bit_digital_status()``.
* Set the bit status and control parameters in ``Model.enter_diagnostic()``.
* Do not report the control status under the state transitoin related commands (except the ``fault()``) in ``Model``.
* Update the ``TabDiagnostics._callback_control_digital_status()`` to check the correct local mode to switch the buttons of digital outputs.
* Update the ``LayoutLocalMode._callback_signal_control()`` that do not show the buttons when the system is doing the mode transition.

.. _lsst.ts.m2gui-0.4.1:

-------------
0.4.1
-------------

* Adapt the **.ts_pre_commit_config.yaml**.

.. _lsst.ts.m2gui-0.4.0:

-------------
0.4.0
-------------

* Update the limit switch status to support the new enum: **Status**.
* Remove the **error_code_m2.tsv** and update the method to get the error code file.
* Update the **Jenkinsfile** to use the default or related branch in **ts_config_mttcs**.
* Fix the data type annotation of **ActuatorForce** class.
* Update the ``TabAlarmWarn.read_error_list_file()`` to use the ``read_error_code_file()`` in **ts_m2com**.
* Separate the **isAlarmWarningOn** overview status to **isAlarmOn** and **isWarningOn** statuses.
* Replace the annotation of ``typing.Set`` with internal ``set``.
* Rename ``Model.add_error()`` to ``Model.report_error()``.
* Differentiate the limit switch is triggered by the software limit or hardware.

.. _lsst.ts.m2gui-0.3.9:

-------------
0.3.9
-------------

* Support the mypy.
* Simplify the **import** method in **__init__.py**.

.. _lsst.ts.m2gui-0.3.8:

-------------
0.3.8
-------------

* Adapt black v23.1.0.

.. _lsst.ts.m2gui-0.3.7:

-------------
0.3.7
-------------

* Select the actuator group to show in the cell map.
* Process the events:
  * tcpIpConnected
  * interlock
  * cellTemperatureHiWarning
  * inclinationTelemetrySource
* Add the **TabIlcStatus** class.
* Adapt black v22.12.0.

.. _lsst.ts.m2gui-0.3.6:

-------------
0.3.6
-------------

* Support the cRIO simulator in the configuration file.
* Issue the load configuration command.
* Export the **PYTEST_QT_API** variable in **Jenkinsfile**.

.. _lsst.ts.m2gui-0.3.5:

-------------
0.3.5
-------------

* Remove the **root** workaround from **Jenkinsfile**.

.. _lsst.ts.m2gui-0.3.4:

-------------
0.3.4
-------------

* Adapt the **ts_tcpip** v1.0.0 to use the **LOCALHOST_IPV4** instead of **LOCAL_HOST**.

.. _lsst.ts.m2gui-0.3.3:

-------------
0.3.3
-------------

* Adapt the **ts_m2com** v0.8.1 to use the commands related to ILC, CLC, etc. directly.
* Remove the dependency of **ts_salobj**.
* Add the **transition_local_mode.uml**.

.. _lsst.ts.m2gui-0.3.2:

-------------
0.3.2
-------------

* Fix the unit test from **ts_m2com** v0.6.3.

.. _lsst.ts.m2gui-0.3.1:

-------------
0.3.1
-------------

* Show the selected actuator force on mirror's view.
* Add the **status** to **enableOpenLoopMaxLimit** command.
* Show the raw and processed inclinometer angles.

.. _lsst.ts.m2gui-0.3.0:

-------------
0.3.0
-------------

* Subscribe the following events:

  * openLoopMaxLimit
  * limitSwitchStatus

* Use the enum of **LimitSwitchType** from **ts_m2com**.

.. _lsst.ts.m2gui-0.2.4:

-------------
0.2.4
-------------

* Separate the buttons to reset the breakers of motor and communication.
* Fix the skipped unit tests on Jenkins.

.. _lsst.ts.m2gui-0.2.3:

-------------
0.2.3
-------------

* Support the specific command, event, and telemetry for the EUI only.
* Add the option to disable the logging file for the file permission issue of CentOS host with the docker container.
In addition, the latest developer docker image has the problem to use the PySide2 with CentOS host as root user.
Report the bug in DM-36459.

.. _lsst.ts.m2gui-0.2.2:

-------------
0.2.2
-------------

* New general settings can be applied anytime/in all states.
* Force-related tables refresh frequency can be modified.
* Default application point size/ scaling can be modified.

.. _lsst.ts.m2gui-0.2.1:

-------------
0.2.1
-------------

* Adapt the **ControllerCell** class in **ts_m2com** to remove the duplicated code.

.. _lsst.ts.m2gui-0.2.0:

-------------
0.2.0
-------------

* Support the parts of command, event and telemetry.
* Support the unit test on TSSW Jenkins instance.
* Output the logging message to file.

.. _lsst.ts.m2gui-0.1.9:

-------------
0.1.9
-------------

* Early simulation mode support.
* Debug level command line argument and settings.

.. _lsst.ts.m2gui-0.1.8:

-------------
0.1.8
-------------

* Add the **.pre-commit-config.yaml**, **pyproject.toml**, and **meta.yaml**.
* Support the **isort**.

.. _lsst.ts.m2gui-0.1.7:

-------------
0.1.7
-------------

* Adapt the **ts_m2com** and **qasync**.
* Begin to support the simulation mode.

.. _lsst.ts.m2gui-0.1.6:

-------------
0.1.6
-------------

* Add the **Jenkinsfile** and publish the built document to `ts_m2gui <https://ts-m2gui.lsst.io>`_.
* Add the documentation.
* Let the **Model** to hold the **SignalControl** instead of the **MainWindow**.

.. _lsst.ts.m2gui-0.1.5:

-------------
0.1.5
-------------

* Support the tool bar.
* Support the table of settings.
* Add the tips.
* Turn off the docker widget features.
* Add the run_application().
* Rename **bin/run_m2gui.py** to **bin/run_m2gui**.

.. _lsst.ts.m2gui-0.1.4:

-------------
0.1.4
-------------

* Support the cell status in part 2. This is to support the realtime figure.

.. _lsst.ts.m2gui-0.1.3:

-------------
0.1.3
-------------

* Add the **cell_geometry.yaml**.
* Support the cell status in part 1. At this moment, the overview of mirror forces is supported.

.. _lsst.ts.m2gui-0.1.2:

-------------
0.1.2
-------------

* Support the actuator control.

.. _lsst.ts.m2gui-0.1.1:

-------------
0.1.1
-------------

* Support the diagnostics.

.. _lsst.ts.m2gui-0.1.0:

-------------
0.1.0
-------------

* Show warning dialog on errors.

.. _lsst.ts.m2gui-0.0.9:

-------------
0.0.9
-------------

* Support the rigid body position.

.. _lsst.ts.m2gui-0.0.8:

-------------
0.0.8
-------------

* Support the detailed force.

.. _lsst.ts.m2gui-0.0.7:

-------------
0.0.7
-------------

* Add the **UtilityMonitor** class.
* Support the utility view.
* Add the *class_tab_utility_view.uml*.
* Rename the *test_config_view.py* to *test_tab_config_view.py*.

.. _lsst.ts.m2gui-0.0.6:

-------------
0.0.6
-------------

* Support the configuration view.
* Add the class diagrams.

.. _lsst.ts.m2gui-0.0.5:

-------------
0.0.5
-------------

* Add the system status and limit switch indicators.
* Add the **FaultManager** class.
* Adapt black v22.3.0.

.. _lsst.ts.m2gui-0.0.4:

-------------
0.0.4
-------------

* Add the UML class diagrams.
* Add the **LayoutDefault** and **TabDefault** classes.
* Implement the alarms/warnings table.

.. _lsst.ts.m2gui-0.0.3:

-------------
0.0.3
-------------

* Add the framework of control tables.
* Implement the overview table.
* Remove the debug messages that are not needed anymore.

.. _lsst.ts.m2gui-0.0.2:

-------------
0.0.2
-------------

* Support the unit test.
* Refactor the control logic.

.. _lsst.ts.m2gui-0.0.1:

-------------
0.0.1
-------------

* Initial upload.
