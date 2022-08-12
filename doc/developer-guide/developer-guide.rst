.. _Developer_Guide:

#########################
Developer Guide
#########################

This GUI is constructed on the top of Qt framework (`Qt for Python <https://wiki.qt.io/Qt_for_Python>`_).

.. _Dependencies:

Dependencies
============

* `ts_salobj <https://github.com/lsst-ts/ts_salobj>`_
* `ts_tcpip <https://github.com/lsst-ts/ts_tcpip>`_
* `ts_utils <https://github.com/lsst-ts/ts_utils>`_
* `ts_config_mttcs <https://github.com/lsst-ts/ts_config_mttcs>`_
* `ts_m2com <https://github.com/lsst-ts/ts_m2com>`_

.. _Architecture:

Architecture
=============

The classes in module are listed below.

.. _lsst.ts.m2gui-modules_m2gui:

m2gui
-----

.. uml:: ../uml/class_m2gui.uml
    :caption: Class diagram of M2 GUI

* **MainWindow** is the main window of the application.
* **Model** contains the main business logic in the application.
* **Config** is a data class that has the configuration details in the M2 cell control system.
* **FaultManager** records the system error.
* **UtilityMonitor** monitors the utility status.
* **ActuatorForce** is a data class that has the force details contain the look-up table (LUT) information, force balance system, etc.
* **ForceErrorTangent** is a data class that is used to monitor the supporting force of mirror according to the tangential link force error.
* **ControlTabs** has the control tables.
* **LogWindowHandler** handles the log window.

The model–view–controller (MVC) architecture is used in this module.
In this design, the view always shows the data sent from the model.
This helps to minimize the business logic in view and makes the tests easier.
If you want to cache the data for a smooth showing in view, you need to do this in the **Model**.

The `Qt signal <https://doc.qt.io/qt-6/signalsandslots.html>`_ is used to do the data exchange.
The `emit()` and `connect()` in the class diagrams mean the class **emits** a specific signal and **connects** it to a specific callback function.
The controller is reused from the `ts_m2com <https://github.com/lsst-ts/ts_m2com>`_.
Most of signals are holded and emitted from the **Model** or its components to simplify the management of signals.
Only the **SignalMessage** is holded by the **MainView**.
The **SignalMessage** is unrelated to the **Model**, which is only used to show the logged message on the overview table.

.. _lsst.ts.m2gui-modules_m2gui_signals:

m2gui.signals
-------------

The available Qt signals are listed below:

* **SignalControl** sends the event that the control is updated or not.
* **SignalError** sends the error code.
* **SignalLimitSwitch** sends the event of limit switch status.
* **SignalMessage** sends the message event.
* **SignalStatus** sends the event of system status.
* **SignalConfig** sends the configuration.
* **SignalUtility** sends the utility status.
* **SignalDetailedForce** sends the calculated and measured force details contains LUT, force balance system, etc.
* **SignalPosition** sends the rigid body position.
* **SignalScript** sends the status of script progress.

.. _lsst.ts.m2gui-modules_m2gui_layout:

m2gui.layout
------------

.. uml:: ../uml/class_layout.uml
    :caption: Class diagram of layout module

* **LayoutDefault** is the default parent panel of other child classes in this module.
* **LayoutControl** is the panel of control.
* **LayoutControlMode** is the panel of control mode.
* **LayoutLocalMode** is the panel of local mode.

.. _lsst.ts.m2gui-modules_m2gui_display:

m2gui.display
-------------

.. uml:: ../uml/display/class_display.uml
    :caption: Class diagram of display module

* **ViewMirror** is the view on the mirror populated by actuators.
* **ItemActuator** is the actuator item used in the **ViewMirror** class to show the actuator information.
* **Gauge** provides the color scale.
* **FigureConstant** is the figure to show the constant line data in real-time.

.. _lsst.ts.m2gui-modules_m2gui_controbtab:

m2gui.controltab
----------------

.. uml:: ../uml/class_controltab.uml
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

The class diagrams for each table child class are listed below to give you the idea of class relationship.

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_actuator_control:

m2gui.controltab.TabActuatorControl
-----------------------------------

.. uml:: ../uml/controltab/class_tab_actuator_control.uml
    :caption: Class diagram of TabActuatorControl class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_alarm_warn:

m2gui.controltab.TabAlarmWarn
-----------------------------

.. uml:: ../uml/controltab/class_tab_alarm_warn.uml
    :caption: Class diagram of TabAlarmWarn class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_cell_status:

m2gui.controltab.TabCellStatus
------------------------------

.. uml:: ../uml/controltab/class_tab_cell_status.uml
    :caption: Class diagram of TabCellStatus class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_config_view:

m2gui.controltab.TabConfigView
------------------------------

.. uml:: ../uml/controltab/class_tab_config_view.uml
    :caption: Class diagram of TabConfigView class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_detailed_force:

m2gui.controltab.TabDetailedForce
---------------------------------

.. uml:: ../uml/controltab/class_tab_detailed_force.uml
    :caption: Class diagram of TabDetailedForce class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_diagnostics:

m2gui.controltab.TabDiagnostics
-------------------------------

.. uml:: ../uml/controltab/class_tab_diagnostics.uml
    :caption: Class diagram of TabDiagnostics class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_overview:

m2gui.controltab.TabOverview
----------------------------

.. uml:: ../uml/controltab/class_tab_overview.uml
    :caption: Class diagram of TabOverview class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_rigid_body_pos:

m2gui.controltab.TabRigidBodyPos
--------------------------------

.. uml:: ../uml/controltab/class_tab_rigid_body_pos.uml
    :caption: Class diagram of TabRigidBodyPos class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_utility_view:

m2gui.controltab.TabUtilityView
-------------------------------

.. uml:: ../uml/controltab/class_tab_utility_view.uml
    :caption: Class diagram of TabUtilityView class

.. _lsst.ts.m2gui-modules_m2gui_controbtab_tab_settings:

m2gui.controltab.TabSettings
----------------------------

.. uml:: ../uml/controltab/class_tab_settings.uml
    :caption: Class diagram of TabSettings class

.. _API:

APIs
=============

This section is autogenerated from docstrings.

.. automodapi:: lsst.ts.m2gui
    :no-inheritance-diagram:
