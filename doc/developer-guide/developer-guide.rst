.. _Developer_Guide:

#########################
Developer Guide
#########################

This GUI is constructed on the top of Qt framework (`Qt for Python <https://wiki.qt.io/Qt_for_Python>`_).

.. _Dependencies:

Dependencies
============

* `ts_idl <https://github.com/lsst-ts/ts_idl>`_
* `ts_tcpip <https://github.com/lsst-ts/ts_tcpip>`_
* `ts_m2com <https://github.com/lsst-ts/ts_m2com>`_

.. _State:

State
=====

The state machine is listed below.

.. mermaid:: ../uml/transition_local_mode.mmd
    :caption: State diagram of local mode.

It is noted that when the fault happens, the **Enable** local mode will transition to the **Diagnostic** local mode.
The other local modes keep the same.

.. _Architecture:

Architecture
=============

The classes in module are listed below.

.. _lsst.ts.m2gui-modules_m2gui:

m2gui
-----

.. mermaid:: ../uml/class_m2gui.mmd
    :caption: Class diagram of M2 GUI

* **MainWindow** is the main window of the application.
* **Model** contains the main business logic in the application.
* **Config** is a data class that has the configuration details in the M2 cell control system.
* **FaultManager** records the system error.
* **UtilityMonitor** monitors the utility status.
* **ActuatorForceAxial** is a data class that has the axial force details contain the look-up table (LUT) information, force balance system, etc.
* **ActuatorForceTangent** is a data class that has the tangent force details contain the look-up table (LUT) information, force balance system, etc.
* **ForceErrorTangent** is a data class that is used to monitor the supporting force of mirror according to the tangential link force error.
* **ControlTabs** has the control tables.
* **LogWindowHandler** handles the log window.

The model–view–controller (MVC) architecture is used in this module.
In this design, the view always shows the data sent from the model.
This helps to minimize the business logic in view and makes the tests easier.
If you want to cache the data for a smooth showing in view, you need to do this in the **Model**.
In accordance with the MVC architecture pattern, the controller reuses the existing module `ts_m2com <https://github.com/lsst-ts/ts_m2com>`_.
This comes with the mock server, which can be used in simulation.

The `Qt signal <https://doc.qt.io/qt-6/signalsandslots.html>`_ is used to do the data exchange.
The `emit()` and `connect()` in the class diagrams mean the class **emits** a specific signal and **connects** it to a specific callback function.
The controller is reused from the `ts_m2com <https://github.com/lsst-ts/ts_m2com>`_.
Most of signals are holded and emitted from the **Model** or its components to simplify the management of signals.
Only the **SignalMessage** is holded by the **MainView**.
The **SignalMessage** is unrelated to the **Model**, which is only used to show the logged message on the overview table.

Qt provides its event loop that is different from the event loop in Python `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library.
The `qasync <https://github.com/CabbageDevelopment/qasync>`_ allows coroutines (`async/await` keywords) to be used in PyQt/PySide applications by providing an implementation of the PEP-3156 event-loop.
For the other tasks in a loop to run, an awaitable must be called from another coroutine.
This allow for the coroutine to claim CPU and performs its operations.
Therefore `await asyncio.sleep()` calls are placed in unit tests calls, so the signal handling etc. can occur.

.. _lsst.ts.m2gui-modules_m2gui_signals:

m2gui.signals
-------------

The available Qt signals are listed below:

* **SignalControl** sends the event that the control is updated or not.
* **SignalPowerSystem** sends the event that the power system is updated or not.
* **SignalError** sends the error code.
* **SignalLimitSwitch** sends the event of limit switch status.
* **SignalMessage** sends the message event.
* **SignalStatus** sends the event of system status.
* **SignalConfig** sends the configuration.
* **SignalUtility** sends the utility status.
* **SignalDetailedForce** sends the calculated and measured force details contains LUT, force balance system, etc.
* **SignalPosition** sends the rigid body position.
* **SignalScript** sends the status of script progress.
* **SignalIlcStatus** sends the status of inner-loop controller (ILC).

.. _lsst.ts.m2gui-modules_m2gui_layout:

m2gui.layout
------------

.. mermaid:: ../uml/class_layout.mmd
    :caption: Class diagram of layout module

* **LayoutDefault** is the default parent panel of other child classes in this module.
* **LayoutControl** is the panel of control.
* **LayoutControlMode** is the panel of control mode.
* **LayoutLocalMode** is the panel of local mode.

.. _lsst.ts.m2gui-modules_m2gui_display:

m2gui.display
-------------

.. mermaid:: ../uml/display/class_display.mmd
    :caption: Class diagram of display module

* **ViewMirror** is the view on the mirror populated by actuators.
* **ItemActuator** is the actuator item used in the **ViewMirror** class to show the actuator information.
* **Gauge** provides the color scale.
* **FigureConstant** is the figure to show the constant line data in real-time.

.. _lsst.ts.m2gui-modules_m2gui_widget:

m2gui.widget
-------------

.. mermaid:: ../uml/class_widget.mmd
    :caption: Class diagram of widget module

* **QMessageBoxAsync** is an asynchronous wrapper for the `QMessageBox <https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMessageBox.html>`_. 
* **QFileDialogAsync** is an asynchronous wrapper for the `QFileDialog <https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QFileDialog.html>`_.

As the standard methods (such as `QDialog exec <https://doc.qt.io/qt-6/qdialog.html#exec>`_) provided by the **PySide2/QtWidgets** library aren't asynchronous (they are synchronous, forcing UI to wait for user action before redrawing UI content) and may spin an additional event loop when called, an asynchronous child is provided.
That makes the `qasync <https://github.com/CabbageDevelopment/qasync>`_ library and its event loop switching trick perform as expected.
Without those wrappers, the UI will be running for the duration of the method call synchronously, not waking up the `asynchronous tasks <https://docs.python.org/3/library/asyncio-task.html#task-object>`_ to react to incoming M2 messages and redrawing widget content.

.. _lsst.ts.m2gui-modules_m2gui_controbtab:

m2gui.controltab
----------------

.. mermaid:: ../uml/class_controltab.mmd
    :caption: Class diagram of controltab module

* **TabDefault** is the default parent table of other child classes in this module.
* **TabActuatorControl** controls the actuator.
* **TabAlarmWarn** shows the alarms and warnings.
* **TabCellStatus** shows the cell status.
* **TabConfigView** shows the configuration in the M2 cell control system.
* **TabDetailedForce** shows the detailed force data.
* **TabDiagnostics** shows the diagnostics information.
* **TabOverview** shows the overview of system status.
* **TabRigidBodyPos** controls the rigid body position.
* **TabUtilityView** shows the utility status.
* **TabSettings** shows the settings of GUI.
* **TabIlcStatus** shows the inner-loop controller (ILC) status.
* **TabNetForceMoment** shows the net force and moment of total actuators and force balance system status.
* **TabRealtimeNetForceMoment** shows the realtime data of net force and moment of total actuators and force balance system status.
* **TabLimitSwitchStatus** shows the limit switch status.
* **TabHardpointSelection** can select the hardpoints.

The class diagrams for each table child class are listed below to give you the idea of class relationship.

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_actuator_control:

m2gui.controltab.TabActuatorControl
-----------------------------------

.. mermaid:: ../uml/controltab/class_tab_actuator_control.mmd
    :caption: Class diagram of TabActuatorControl class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_alarm_warn:

m2gui.controltab.TabAlarmWarn
-----------------------------

.. mermaid:: ../uml/controltab/class_tab_alarm_warn.mmd
    :caption: Class diagram of TabAlarmWarn class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_cell_status:

m2gui.controltab.TabCellStatus
------------------------------

.. mermaid:: ../uml/controltab/class_tab_cell_status.mmd
    :caption: Class diagram of TabCellStatus class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_config_view:

m2gui.controltab.TabConfigView
------------------------------

.. mermaid:: ../uml/controltab/class_tab_config_view.mmd
    :caption: Class diagram of TabConfigView class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_detailed_force:

m2gui.controltab.TabDetailedForce
---------------------------------

.. mermaid:: ../uml/controltab/class_tab_detailed_force.mmd
    :caption: Class diagram of TabDetailedForce class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_diagnostics:

m2gui.controltab.TabDiagnostics
-------------------------------

.. mermaid:: ../uml/controltab/class_tab_diagnostics.mmd
    :caption: Class diagram of TabDiagnostics class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_overview:

m2gui.controltab.TabOverview
----------------------------

.. mermaid:: ../uml/controltab/class_tab_overview.mmd
    :caption: Class diagram of TabOverview class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_rigid_body_pos:

m2gui.controltab.TabRigidBodyPos
--------------------------------

.. mermaid:: ../uml/controltab/class_tab_rigid_body_pos.mmd
    :caption: Class diagram of TabRigidBodyPos class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_utility_view:

m2gui.controltab.TabUtilityView
-------------------------------

.. mermaid:: ../uml/controltab/class_tab_utility_view.mmd
    :caption: Class diagram of TabUtilityView class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_settings:

m2gui.controltab.TabSettings
----------------------------

.. mermaid:: ../uml/controltab/class_tab_settings.mmd
    :caption: Class diagram of TabSettings class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_ilc_status:

m2gui.controltab.TabIlcStatus
-----------------------------

.. mermaid:: ../uml/controltab/class_tab_ilc_status.mmd
    :caption: Class diagram of TabIlcStatus class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_net_force_moment:

m2gui.controltab.TabNetForceMoment
----------------------------------

.. mermaid:: ../uml/controltab/class_tab_net_force_moment.mmd
    :caption: Class diagram of TabNetForceMoment class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_hardpoint_selection:

m2gui.controltab.TabHardpointSelection
--------------------------------------

.. mermaid:: ../uml/controltab/class_tab_hardpoint_selection.mmd
    :caption: Class diagram of TabHardpointSelection class

.. _API:

APIs
=============

This section is autogenerated from docstrings.

.. automodapi:: lsst.ts.m2gui
    :no-inheritance-diagram:
