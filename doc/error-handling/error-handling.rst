.. _Error_Handling:

################
Error Handling
################

The error codes and related details are listed in `here <https://github.com/lsst-ts/ts_config_mttcs/blob/develop/MTM2/v2/error_code.tsv>`_.
When the error happens, you can follow the document of **LSST M2 Controller ICD_revB (T14900-0124)** for the possible action to fix the M2 system.
For the simplicity, list the details in :ref:`lsst.ts.m2gui-error_troubleshooting`.
In some cases, you may need to restart the application in cRIO.
You can follow the :ref:`lsst.ts.m2gui-error_restart_control_system` to do so.
The log file in cRIO can support the debug as well.
See :ref:`lsst.ts.m2gui-error_log_file` for the details.
Sometimes, the errors are not real or easy to fix compared with the steps in :ref:`lsst.ts.m2gui-error_troubleshooting`.
There special cases are documented in :ref:`lsst.ts.m2gui-error_special_cases`.

.. _lsst.ts.m2gui-error_restart_control_system:

Restart Control System
======================

There are two cRIO controllers (``m2-crio-controller01.cp.lsst.org`` and ``m2-crio-controller02.cp.lsst.org``) on the summit and one cRIO simulator (``m2-crio-simulator.ls.lsst.org``) in the base data center.
Before the restart of control system, check with the hardware engineers which cRIO is the right one to reboot.
All the IP addresses, accounts, and passwords are recorded in `1Passoword MainTel Vault <https://lsstit.1password.com/signin>`_.

You can log in the controller by ``ssh``:

.. code:: bash

    ssh ${account}@${ip}

Based on the OS platform, sometimes, you may need to do the following instead:

.. code:: bash

    ssh -o "PubkeyAuthentication=no" ${account}@${ip}

After the login, you will be under the ``/home/admin`` directory.
The running command of control system is: ``{MainAppThread} ./lvrt``, and you can use the ``top`` command to check it.
Usually, the related CPU usage is 5% at standby and 10-25% at running.
If the CPU usage is 50% or higher, that means there is the dead-lock happens in the application and you do need to restart the application.

To do so, you need to stop the running application first:

.. code:: bash

    /etc/init.d/nilvrt stop

Wait for some time such as 3 minutes to make sure the application stops completely.
Start the control system by the following command:

.. code:: bash

    /etc/init.d/nilvrt start

This process will take around 3 minutes.
A new log file will be generated, and you can see :ref:`lsst.ts.m2gui-error_log_file` for the details.
It is noted that you will see 0% CPU usage of the application in the starting process for some time period.
This is because the control system need 60 seconds to load the FPGA bit file at that period.
After that, you should expect to see around 5% CPU usage of the application.
If not, something is wrong and you can check the log file for the details.

.. _lsst.ts.m2gui-error_log_file:

Log File
========

You need to log in the controller by following :ref:`lsst.ts.m2gui-error_restart_control_system`.
The log files are in the ``/u/log`` directory.
The name of log file is based on the time when the control system starts the running.
You can search the keyword such as **error** or others in the file by:

.. code:: bash

    grep -nr "error" ${logFile}

If the application runs successfully, you should see something similar as the followings in the beginning of log file:

.. code::

    2023-08-31T07:12:02.789+00:00,DAQ process launched and should be running (paused state).
    2023-08-31T07:12:02.885+00:00,Power control subsystem process launched and should be running (off state).
    2023-08-31T07:12:02.957+00:00,Network interface process launched and should be running.
    2023-08-31T07:12:03.035+00:00,TCP/IP interface process for GUI launched and should be running.
    2023-08-31T07:12:46.540+00:00,M2 Controller has connected to the cRIO.

The log file will show the configuration files in use as something similar below as well:

.. code::

    2023-08-30T08:56:38.676+00:00,Load the system configuration file: /home/lvuser/natinst/config/sysconfig/Configurable_File_Description_20180831T092556_surrogate_handling.csv
    2023-08-30T08:56:38.847+00:00,Load the cell mapping file: /home/lvuser/natinst/config/system/cell/cell-actuator_mapping_file.xml
    2023-08-30T08:56:38.930+00:00,Load the home position file: /home/lvuser/natinst/config/home_position.xml
    2023-08-30T08:56:39.013+00:00,Load the IMS file: /home/lvuser/natinst/config/dispIMS.json

As a reference, the ``/u`` directory has the softlinks with ``/home/lvuser/natinst`` directory as the following:

.. code::

    admin@NI-cRIO-9049-01EAEB52:/u# ls -al .
    total 8
    drwxr-xr-x    2 admin    administ      4096 Jun  7 06:54 ./
    drwxr-xr-x   20 admin    administ      4096 Aug 31 07:10 ../
    lrwxrwxrwx    1 admin    administ        28 Jun  7 06:53 config -> /home/lvuser/natinst/config//
    lrwxrwxrwx    1 admin    administ        25 Jun  7 06:53 log -> /home/lvuser/natinst/log//
    lrwxrwxrwx    1 admin    administ        28 Jun  7 06:54 script -> /home/lvuser/natinst/script//

.. _lsst.ts.m2gui-error_troubleshooting:

Troubleshooting
================

When the error happens, you can check the **Troubleshooting Next Steps** in the following table to fix the issue (based on **T14900-0124**).
Sometimes, the alarms/warnings on GUI might be out-of-date, and you can try to reset them first (see :ref:`lsst.ts.m2gui-user_alarm_warn`) before the further action.

.. list-table:: Troubleshooting
   :widths: 10 40 70 120
   :header-rows: 1

   * - Code
     - Failure
     - Cause of Error
     - Troubleshooting Next Steps
   * - 6051
     - Actuator inner-loop controller (ILC) read error
     - ILC responded with an exception code, did not respond at all (timeout), did not receive command, or reported fault status.
     - Most likely an ILC that is not responsive/failed. Look at the telemetry data to see which ILC address does not show a correct broadcast counter that increments by 16 every time step. That will narrow down the ILC to troubleshoot. If an ILC needs to be replaced, reference **T14900-1002** ILC Programming Document to reprogram and configure the software properly. Check the :ref:`lsst.ts.m2gui-error_code_6051_6088` as well.
   * - 6052
     - Monitoring ILC read error
     - ILC responded with an exception code or did not respond at all (timeout).
     - The current firmware of the sensor ILCs generate this warning 4.5% of all samples. Updating to new firmware on the sensor ILCs should remedy this warning. For reference, updating firmware on the ILCs is described in **T14900-1002** ILC Programming Document.
   * - 6053
     - cRIO communication error
     - Loss of communication between the cRIO and M2 controller.
     - Check to see if the power is lost to the cRIO. Check the internet connection between the switch and cRIO. Check there is the internet traffic jam or not.
   * - 6054
     - ILC state transition error
     - Internal ILC issue. ILC did not change state.
     - Most likely an ILC that is not responsive/failed during startup. The log file will describe which addresses violates the state transition timing. Look at the first address which failed to meet timing. If it is determined that an ILC needs to be replaced, reference **T14900-1002** ILC Programming Document to reprogram and configure the software properly.
   * - 6055
     - Excessive force detected
     - Measured force exceeded programmable threshold.
     - Reference the `constant.py <https://github.com/lsst-ts/ts_m2com/blob/develop/python/lsst/ts/m2com/constant.py>`_ to determine the force limits for the state when the excessive force was detected. Look at the :ref:`lsst.ts.m2gui-user_actuator_control` or :ref:`lsst.ts.m2gui-user_detailed_force` to determine the actuator(s) which violated the force limits. In **Local** mode, drive the actuator(s) away from the force limit. If the excessive force was originally detected in open-loop, click the **Enable Open-Loop Max Limits** button to provide force relief to unload the actuators. If for some reason it is determined that the load cell has been compromised and needs to be replaced, reference **T14900-3024** Axial Actuator Replacemement. If this error is triggered from the rigid body movement, see the :ref:`lsst.ts.m2gui-recover_system_from_rigid_body_movement`.
   * - 6056
     - Actuator limit switch triggered [closed-loop]
     - An actuator responded with a closed limit switch in any direction.
     - Check to see on the :ref:`lsst.ts.m2gui-user_limit_switch_status` which actuator(s) has triggered limit switches. Go into manual open-loop mode to drive the offending actuator(s) off the limits. If both the extend and retract limit switches indicate they have been closed, a communication error has occurred with that ILC and a power-cycle of system might be required.
   * - 6057
     - Actuator limit switch triggered [open-loop]
     - Same as error 6056.
     - Same as error 6056.
   * - 6058
     - Inclinometer error [fault]
     - Communication error or the ILC reported fault.
     - Check inclinometer sensor ILC for errors/disconnections.
   * - 6059
     - Inclinometer error [warning]
     - Same as error 6058.
     - Same as error 6058.
   * - 6060
     - Inclinometer difference error
     - Excessive angular difference between the external and local inclinometers.
     - Check to see if local inclinometer has come loose from cell. Ensure the external elevation is correct and calibrated. If necessary, reference **T14900-0132** Inclinometer Calibration to recalibrate the local M2 inclinometer.
   * - 6061
     - Motor power supply(s) over/under voltage [fault]
     - Measured voltage exceeds programmable limits (2-sided).
     - Using proper electrostatic discharge (ESD) protocols, inspect the motor power cables for any possible soft or hard shorts.
   * - 6062
     - Motor power supply(s) over/under voltage [warning]
     - Same as error 6061.
     - Same as error 6061.
   * - 6063
     - Comm power supply(s) over/under voltage [fault]
     - Measured voltage exceeds programmable limits (2-sided).
     - Using proper electrostatic discharge (ESD) protocols, inspect the communicaton power cables for any possible soft or hard shorts.
   * - 6064
     - Comm power supply(s) over/under voltage [warning]
     - Same as error 6063.
     - Same as error 6063.
   * - 6065
     - Excessive motor current
     - Measured current exceeds programmable limit (1-sided).
     - Run the actuator bump test and look at the telemetry to see if any one actuator is causing the motor bus current to spike when moving. That could indicate an issue in that actuator's drivetrain and would need to be replaced. Using proper electrostatic discharge (ESD) protocols, inspect the motor power cables for any possible soft or hard shorts. Check the :ref:`lsst.ts.m2gui-error_code_6065_6066` as well.
   * - 6066
     - Excessive comm current
     - Same as error 6065.
     - Same as error 6063. Check the :ref:`lsst.ts.m2gui-error_code_6065_6066` as well.
   * - 6067
     - Power relay opening fault
     - Power relay did not open when commanded by software.
     - Some latency in the power relay opening is causing this fault. Could be caused by a faulty relay, a slowly changing condition could also be slowing down the opening of the relays. If necessary, the power relay opening threshold can be increased in software.
   * - 6068
     - Power supply health fault
     - Binary outputs signal power supply health fault.
     - Binary signal that indicates the self-health monitoring within the power supplies have detected an issue. Repair or replace the offending power supply.
   * - 6069
     - Multi-breaker trip on same comm power feed
     - Breaker feedback showed two or more breaker trips.
     - Same as error 6063.
   * - 6070
     - Multi-breaker trip on same motor power feed
     - Same as error 6069.
     - Same as error 6061.
   * - 6071
     - Single breaker trip
     - Breaker feedback showed single breaker trip.
     - Same as errors 6061 and 6063.
   * - 6072
     - Power supply load sharing error
     - Based on binary output from redundancy module.
     - Could be caused by a bad power supply redundancy module or an actual mismatch in power supply load sharing. If the power supplies are not contributing equal loading, it may also be possible that the power supply health fault could be seen (error 6068). In either case, try replacing the redundancy module or using different power supplies.
   * - 6073
     - cRIO 50 msec cycle time monitor [fault]
     - Measured loop time exceeded 50 ms for three consecutive cycles.
     - Look for additional processes that could be costing computation time on the cRIO.
   * - 6074
     - cRIO 50 msec cycle time monitor [Warning]
     - Measured loop time exceeded 50 ms for one cycle.
     - Look for additional processes that could be costing computation time on the cRIO.
   * - 6075
     - Excessive cell temperature differential
     - Intake-exhaust temperature diff exceeds programmable threshold.
     - Look at the :ref:`lsst.ts.m2gui-user_diagnostics` to see what the intake/exhaust temperatures are reading. Reference the :ref:`lsst.ts.m2gui-user_configuration_view` to see what the temperature threshold is set to. Ensure threshold is set reasonably. Increase threshold if necessary. Otherwise, look for blockage in the exhaust path of the cell assembly.
   * - 6077
     - Configurable parameter file read error
     - The software cannot properly read in the file or something is corrupted with the data read from the file.
     - Check the ``/u/config`` directory to ensure all files are present and not corrupt. Reference **T14900-1005** Configurable File Description Document to find all the necessary files and LUTs.
   * - 6078
     - Displacement sensor out of range
     - Sensor value out of range.
     - Most likely a failure of the displacement sensor. Look in the :ref:`lsst.ts.m2gui-user_utility_view` to determine which displacement sensor is out of range. First inspect the sensor ILC associated with the offending displacement sensor. Ensure wiring is correct. Manually move the failed displacement sensor while monitoring the :ref:`lsst.ts.m2gui-user_utility_view` to determine if any valid readings are received. If not, it could be necessary to replace the displacement sensor or the sensor ILC.
   * - 6079
     - Inclinometer out of range
     - Same as error 6078.
     - Unlikely failure to happen. If an inclinometer sensor ILC had trouble commmunicating, the inclinometer warning/fault would be tripped. This fault is designed to ensure the inclination value received is within range.
   * - 6080
     - Mirror temperature sensor out of range [fault]
     - Same as error 6078.
     - Most likely a failure of the temperature sensor. Look in the :ref:`lsst.ts.m2gui-user_utility_view` to determine which mirror temperature sensor is out of range. First inspect the sensor ILC associated with the out of range sensor. Since the mirror temperature sensors are bonded to the mirror, alternative methods for replacing that signal must be explored.
   * - 6082
     - Airflow temperature sensor out of range
     - Same as error 6078.
     - Most likely a failure of the temperature sensor. Look in the :ref:`lsst.ts.m2gui-user_utility_view` to determine which airflow temperature sensor is out of range. On the cell, inspect that offending airflow temperature sensor and replace if necessary.
   * - 6083
     - Axial actuator encoder out of range
     - Same as error 6078.
     - Most likely a failure of the encoder sensor. Look in the :ref:`lsst.ts.m2gui-user_detailed_force` to find the offending axial actuator. Inspect the wiring of the encoder of that actuator as well as the actuator ILC to ensure proper connects.
   * - 6084
     - Tangent actuator encoder out of range
     - Same as error 6078.
     - Most likely a failure of the encoder sensor. Look in the :ref:`lsst.ts.m2gui-user_detailed_force` to find the offending tangent actuator. Inspect the wiring of the encoder of that actuator as well as the actuator ILC to ensure proper connects.
   * - 6088
     - Tangent load cell fault
     - Tangent load cell calculations violate any of the monitoring conditions.
     - Possible causes: tangent actuator ILC, tangent actuator load cell, tangent actuator ILC wiring, bad inclination signal. If it is determined that a tangent actuator is to be replaced, reference **T14900-3025** Tangent Actuator Replacement. If an ILC needs to be replaced, reference **T14900-1002** ILC Programming Document. Check the :ref:`lsst.ts.m2gui-error_code_6051_6088` as well. If this error is triggered from the rigid body movement, see the :ref:`lsst.ts.m2gui-recover_system_from_rigid_body_movement`.

.. _lsst.ts.m2gui-error_special_cases:

Special cases
==============

The special cases of error handling are listed below.

.. _lsst.ts.m2gui-error_connection_timeout:

Connection Timeout
-------------------

If you have the connection timeout, you can try to ``ping`` the controller first by:

.. code:: bash

    ping ${ip}

The next step is to check the commandable SAL component (CSC) has the connection with the controller or not.
Before the fix of `DM-37422 <https://jira.lsstcorp.org/browse/DM-37422>`_, you can only have one client (GUI or CSC) to the controller.
If the CPU usage of application has 50% or higher, this will block the connection and you can follow :ref:`lsst.ts.m2gui-error_restart_control_system` to fix it.

In addition, if there is no enough disk space in controller, it will block the connection as well.
Although there is the ``crontab`` job in controller to clean the log files regularly, it would be worthful for you to check the files and related sizes in the ``/u/log`` directory in controller.
If none of above is the reason, you could always try to restart the application as the final solution.

.. _lsst.ts.m2gui-error_code_6051_6088:

Code 6051 and 6088
-------------------

These two error codes might not be real and you could try the followings first:

1. Restart the control system.
2. Power-cycle the whole M2 system.

In addition, they might happen when you have the inconsistent elevation angle and look-up table (LUT) calculation.
For example, if the following actions are executed:

1. Put the system into the closed-loop control at 20 degree elevation angle.
2. Turn off the force balance system by transition to the open-loop control, **Standby/Diagnostic** state, shutdown the system, or something similar.
3. Move the M2 to another elevation angle such as 30 degree by the cart or telescope mount assembly (TMA).

Most likely, when you try to transition to the **Enabled** state or closed-loop control, you will get the error codes of 6051 or 6088 immediately.
When this happens, you just need to move the M2 back to the original elevation angle (20 degree in this example), and you should be able to enable the system again.
If you forget the original elevation angle, you may need to check the engineering facility database (EFD), try-and-error, or calculate the possible elevation angle based on the measured forces at that moment.

.. _lsst.ts.m2gui-error_code_6065_6066:

Code 6065 and 6066
-------------------

These two error codes might not be real because the related judgement in controller is based on the power thresholds in the configuration file:

1. 24V Accuracy Warning
2. 24V Accuracy Fault
3. Current Threshold

The first step to debug is to check the thresholds in configuration make sense or not.
If they are, you may need to check the power supplies in hardware.

The power to the motors and ILCs (for telemetry) goes from the cabinet to the M2 cell using 3 cables.
The 78 actuators are grouped by 3 cables (or zones) and every cable powers the motors and ILCs to 26 actuators.
If the error was **Excessive Comm Current (code 6066)**, this means the telemetry was consuming more than expected.
If one actuator was failing, it would imply the overcurrent would be seen on only one cable.
Therefore, if you test one cable (or zone) at one time, you should be able to identify which group of actuators might have the power issue.
But if the error kept the same for all 3 zones, it would imply a failure in every one of 3 zones, which was highly unlikely to be the case, and you might need to check something else that might result in these errors.

.. _lsst.ts.m2gui-recover_system_from_rigid_body_movement:

Recover the System from the Rigid Body Movement
-----------------------------------------------

The available range of rigid body momement is restricted to the assembly and it would induce the error codes: 6055 and 6088 if the movement is big.
Actually, in the normal telescope survey, the M2 should stay at the origin with the minimum stress.
However, in some cases, we would need to adjust the mirror's position and this might trigger the error to transition the system to leave the closed-loop control to protect the mirror.

If the error code is 6055, you can check the :ref:`lsst.ts.m2gui-user_detailed_force` to see which actuator has the force higher than the threshold of closed-loop control.
Usually, the axial actuator is related to the z-direction and the tangent link is related to the x- and y-direction.
Once the actuator is identified, you can move it in steps to have the force lower than the threshold of closed-loop control, and then, put the system into the closed-loop control to recover the system.
It is noted that the single actuator movement will increase the stress of the system.
Therefore, the actuator's force should not differ from the threshold too much before transitioning to the closed-loop control.
Otherwise, the system might be damaged from the high stress.

If the error code is 6088, it might be easier to bypass this error code first, and move the system back to the origin directly to minimize the moment in the movement.
See :ref:`lsst.ts.m2gui-user_alarm_warn` for the details.
But the action to bypass the error code might break the system totally.
Therefore, it would be better to check with the maintainers first before bypassing the error code.
