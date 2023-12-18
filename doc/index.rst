.. |developer| replace:: *Te-Wei Tsai <ttsai@lsst.org>*
.. |product_owner| replace:: *Sandrine Thomas <sthomas@lsst.org>*

.. Note that the ts_ prefix is omitted from the title

########################
M2 GUI
########################

.. image:: https://img.shields.io/badge/GitHub-ts__m2gui-green.svg
    :target: https://github.com/lsst-ts/ts_m2gui
.. image:: https://img.shields.io/badge/Jenkins-ts__m2gui-green.svg
    :target: https://tssw-ci.lsst.org/job/LSST_Telescope-and-Site/job/ts_m2gui
.. image:: https://img.shields.io/badge/Jira-ts__m2gui-green.svg
    :target: https://jira.lsstcorp.org/issues/?jql=labels%20in%20(ts_m2gui%2C%20%20M2)

.. _Overview:

Overview
========

This module is the M2 graphical user interface (GUI) in Python under the Qt framework.
This is to replace the original GUI in LabVIEW (`ts_mtm2 <https://github.com/lsst-ts/ts_mtm2>`_).
The `eups <https://github.com/RobertLuptonTheGood/eups>`_ is used as the package manager.

The badges above navigate to the GitHub repository for the GUI code and Jira issues.

.. _Configuration:

Configuring the M2 GUI
======================

The M2 GUI configuration is `here <https://github.com/lsst-ts/ts_config_mttcs/blob/develop/MTM2/v2/default_gui.yaml>`_.
The yaml file is used and read when the application runs.
You can also use the setting table in GUI to update the values.
See the :ref:`user guide <User_Documentation>` for the details.

.. _User_Documentation:

User Documentation
==================

Observatory operators and other interested parties should consult the user guide for insights into the M2 GUI operations.

.. toctree::
    user-guide/user-guide
    :maxdepth: 1

.. _Error_Handling_Documentation:

Error Handling Documentation
============================

The possible error of M2 and the related handling to recover the system are recorded here.

.. toctree::
    error-handling/error-handling
    :maxdepth: 1

.. _Development_Documentation:

Development Documentation
=========================

Classes and their methods are described in this section.

.. toctree::
    developer-guide/developer-guide
    :maxdepth: 1

.. _Version_History:

Version History
===============

The version history is at the following link.

.. toctree::
    version_history
    :maxdepth: 1

The released version is `releases <https://github.com/lsst-ts/ts_m2gui/releases>`_.

Contributing
============

To contribute, please start a new pull request on `GitHub <https://github.com/lsst-ts/ts_m2gui>`_.
Feature requests shall be filled in JIRA with the *ts_m2gui* or *M2* label.
In all cases, reaching out to the :ref:`contacts for this <Contact_Personnel>` is recommended.

.. _Contact_Personnel:

Contact Personnel
=================

For questions not covered in the documentation, emails should be addressed to the developer: |developer|.
The product owner is |product_owner|.

This page was last modified |today|.
