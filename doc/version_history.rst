.. py:currentmodule:: lsst.ts.m2gui

.. _lsst.ts.m2gui-version_history:

##################
Version History
##################

.. _lsst.ts.m2gui-1.1.8:

-------------
1.1.8
-------------

* Simplify the ``setup.py``.

.. _lsst.ts.m2gui-1.1.7:

-------------
1.1.7
-------------

* Add the **QT_QPA_PLATFORM** to ``meta.yaml`` to fix the test section of conda recipe.

.. _lsst.ts.m2gui-1.1.6:

-------------
1.1.6
-------------

* Run the ``Model._basic_cleanup_and_power_off_motor()`` in ``Model.fault()`` as an asynchronous task to avoid the break of logic to turn off the motor power when there is the fault found in ``Model._process_event()``, which is a callback function.

.. _lsst.ts.m2gui-1.1.5:

-------------
1.1.5
-------------

* Improve the ``setup.py`` to support the version of Python 3.11 and 3.12.

.. _lsst.ts.m2gui-1.1.4:

-------------
1.1.4
-------------

* Fix the failed unit test because of the update of **ts_guitool**.

.. _lsst.ts.m2gui-1.1.3:

-------------
1.1.3
-------------

* Remove the **ts_idl**.

.. _lsst.ts.m2gui-1.1.2:

-------------
1.1.2
-------------

* Use the ``update_button_color()`` and ``create_double_spin_box()`` in **ts_guitool** v0.2.1.

.. _lsst.ts.m2gui-1.1.1:

-------------
1.1.1
-------------

* Adapt the **ts_guitool** v0.2.0.

.. _lsst.ts.m2gui-1.1.0:

-------------
1.1.0
-------------

* Adapt the **ts_guitool**.

.. _lsst.ts.m2gui-1.0.3:

-------------
1.0.3
-------------

* By default, bypass the ILC read warning codes.
* Fix the bug of ``QFileDialogAsync.get_open_filename_async()``.

.. _lsst.ts.m2gui-1.0.2:

-------------
1.0.2
-------------

* Do not calculate the temperature LUT by default.

.. _lsst.ts.m2gui-1.0.1:

-------------
1.0.1
-------------

* Improve the **README.md**.
* Update the ``MainWindow._callback_disconnect()`` to check the current commander.
* Add the ``SignalClosedLoopControlMode`` and update ``Model._process_event()`` to send the signal.
* Add the ``TabOverview._set_signal_closed_loop_control_mode()``. 
* Add the ``TabIlcStatus._is_closed_loop_control_mode_in_idle()``.
* Update the **TabDiagnostics** to support the control of closed-loop control mode.
* Add the ``TabSettings._callback_time_out()`` to write the external elevation angle continuously.
* Update the user manual and UML diagrams.

.. _lsst.ts.m2gui-1.0.0:

-------------
1.0.0
-------------

* Adapt the **PySide6**.

.. _lsst.ts.m2gui-0.7.9:

-------------
0.7.9
-------------

* Update the ``TabIlcStatus`` class to reset, check, and enable the ILC states.
* Update the ``LayoutControl._callback_signal_control()`` to switch the command source under the **Standby** and **Enable** states.
* Add the return values to ``Model.enter_diagnostic()`` and ``Model.enter_enable()`` to judge the CSC is using the M2 or not.
* Update the user documents.

.. _lsst.ts.m2gui-0.7.8:

-------------
0.7.8
-------------

* Bypass the actions if the CSC is connecting to the controller.
* Update the ``LayoutControlMode._callback_signal_control()`` to show the open/closed loop control mode in the **Standby** state as well.
This is to consider the case that the CSC might be using the M2 system at the same time.

.. _lsst.ts.m2gui-0.7.7:

-------------
0.7.7
-------------

* Use the shared Jenkins library in **Jenkinsfile**.

.. _lsst.ts.m2gui-0.7.6:

-------------
0.7.6
-------------

* Update the version of ts-conda-build to 0.4 in the conda recipe.
* Use the **ILC_READ_WARNING_ERROR_CODES** from **ts_m2com**.
* Show the bypassed ILCs.
* Allow to enable or disable the temperature LUT.
* Allow the set of hardpoints.

.. _lsst.ts.m2gui-0.7.5:

-------------
0.7.5
-------------

* Use the **mermaid** to replace the **PlantUML**.

.. _lsst.ts.m2gui-0.7.4:

-------------
0.7.4
-------------

* Properly report connection timeout error.

.. _lsst.ts.m2gui-0.7.3:

-------------
0.7.3
-------------

* Update the ``TabDiagnostics._get_list_digital_status_output()``.

.. _lsst.ts.m2gui-0.7.2:

-------------
0.7.2
-------------

* Add the ``recover-system-night.rst``.
* Improve the document.

.. _lsst.ts.m2gui-0.7.1:

-------------
0.7.1
-------------

* Adapt the update in **ts_m2com**.

.. _lsst.ts.m2gui-0.7.0:

-------------
0.7.0
-------------

* Add the **tab_hardpoint_selection.py**.
* Improve the user manual.

.. _lsst.ts.m2gui-0.6.10:

-------------
0.6.10
-------------

* Improve the document of error handling.

.. _lsst.ts.m2gui-0.6.9:

-------------
0.6.9
-------------

* Improve the documents to power cycle the system and release the interlock.

.. _lsst.ts.m2gui-0.6.8:

-------------
0.6.8
-------------

* Improve the documents.

.. _lsst.ts.m2gui-0.6.7:

-------------
0.6.7
-------------

* Fix the ``test`` section of ``meta.yaml``.
* Update the ``.ts_pre_commit_config.yaml``.

.. _lsst.ts.m2gui-0.6.6:

-------------
0.6.6
-------------

* Remove the legacy code.
* Use the enums in **ts_xml** instead of **ts_idl**.

.. _lsst.ts.m2gui-0.6.5:

-------------
0.6.5
-------------

* Improve the user manual and add the section of error handing.
* Fix the format of code.

.. _lsst.ts.m2gui-0.6.4:

-------------
0.6.4
-------------

* Use the enums in **ts_idl**.

.. _lsst.ts.m2gui-0.6.3:

-------------
0.6.3
-------------

* Add the **Jenkinsfile.conda** and **setup.py**.
* Move the policy files to **ts_config_mttcs**.
* Remove the ``log/`` directory and output the log file to ``/rubin/mtm2/log`` if possible.
* Remove the argument of ``run_application()``.
* Workaround the Python 3.11 issue in **qasync** module.

.. _lsst.ts.m2gui-0.6.2:

-------------
0.6.2
-------------

* Bypass the ILC reading error codes temporarily before upgrading the ILC firmware.
* Update the layout of **TabAlarmWarn**.
* Add the functions to analyze the lost ILC communication in log file.
* Add the **TabLimitSwitchStatus** class.
* Rename the indicator: **isInterlockEnabled** to be **isInterlockEngaged**.

.. _lsst.ts.m2gui-0.6.1:

-------------
0.6.1
-------------

* Handle the error in ``Model.enter_enable()`` when failed to enable all the ILCs.
* Allow to bypass the state check of ``Model.command_script()``.
* Turn on the communication power at ``Model.enter_enable()`` instead of ``Model.enter_diagnostic()``.
* Finetune the behavior and timeout for functions relate to the state transition.
* Fix the typo in **TabDiagnostics** and **UtilityMonitor** classes.
* User can set the retry times and timeout of the ILC state transition.
* Filter the outlier of raw inclinometer value.

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

* Rename the "isInterlockOn" with "isInterlockEnabled" to be consistent with the controller. The indicator's color should be green instead of red when the status is on.
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
* Add the option to disable the logging file for the file permission issue of CentOS host with the docker container. In addition, the latest developer docker image has the problem to use the PySide2 with CentOS host as root user. Report the bug in DM-36459.

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
