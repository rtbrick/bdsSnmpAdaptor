.. VN-IP2-Testlab documentation master file, created by
   sphinx-quickstart on Tue Feb 19 20:00:22 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Change History and todolist
===========================

.. list-table:: Change History Table
   :widths: 10 10 10 70
   :header-rows: 1

   * - Release
     - Date
     - Author
     - Description
   * - 0.5
     - 18.2.19
     - SLi
     - | initial release, using reStructuredText markup syntax
       | change of runbook directory from vIP2 to VN-IP2-Testlab and other naming convention changes.
       | IPv4_popLinks_ranges - deprecation of differentiation between intra-pop and inter-pop IPv4 _setupIpAddresses
       | deprecation of interPoPLinkReserve attribute,
       |  now automatically calculated.
       |  Provisioning order: intra-PoP -> inter-PoP -> external
       | changes for multiple SW releases: vmModels container contains attributes
       |   for referencing vmdk release. Although it is currently not used, vmModels
       |   offers also the possibility to reference specific vmx files.
   * - 0.53
     - 22.2.19
     - SLi
     - | update on Esxi OVA import
       | update on Esxi .vmx repo.
       | deprecate hostDict references for esxi runbooks. All device access
       |   parameters are listed explicitly for each test step.
       | added chapter topologyCreationWorkflow
   * - 0.62
     - 9.3.19
     - SLi
     - | added KVM orchestration section
       | added section for documentation
       | added chapter topologyCreationWorkflow
   * - 0.63
     - 15.3.19
     - SLi
     - | deprecate tE3Settings.runbookDir automatically detected from topology name
       | auto create of runbook dir, no need for manual creation
       | added convenience shell script for setups and destroy

.. todolist::

.. toctree::

   overview
   topologyCreationWorkflow
   runbookGenerator
   testExecutor
   l2Provisioning
   vRouterGenericParts
   vRouterProvisioningScope
   ESXivRouterImageRespositories
   KvmvRouterImageRespositories
   resourceManagement
   pythonClassesAndModules

sphinx doc. structure
=====================

This documentation is created by use of the sphinx tool, which uses
reStructuredText (reST) markup text-input documents, which may include text segments
which are embedded in python docstring
python

.. image:: images/sphinxDoc.png
   :align:   center
   :width: 100%
   :scale: 95%

All sphinx input files are included in the git-Repo for VN-IP2-Testlab, thus the
regular git pull/modify/push can be applied for modification of the documentation
source.

A system (testexecutor VM), which has sphinx application installed is to compile the
reST input files to HTML and PDF outputs.

.. code:: sh

    $ cd TA/VN-IP2-Testlab
    $ ls -la Makefile
    -rw-r--r--  1 sli  staff  631  7 Mär 20:55 Makefile
    $ make html
    Sphinx v1.8.3 in Verwendung
    ...
    Output written on VN-IP2-Testlab.pdf (76 pages, 1256078 bytes).
    ...

.. code:: sh

    $ make latexpdf
    Sphinx v1.8.3 in Verwendung
    ....
    The HTML pages are in sphinxBuild/html.

.. list-table:: sphinx documentation files
   :widths: 20 10 70
   :header-rows: 1

   * - File
     - Type
     - Description
   * - Makefile
     - .
     - includes the configurations for the make command, e.g. in/out
       directories and python syntax interpreter to v3.
   * - conf.py
     - python
     - this is the main configuration file of sphinx and contains information
       on python modules, templates and add-ons
   * - sphinxSource/index.rst
     - reST
     - main file for documentation source content.
   * - sphinxSource/_.rst
     - reST
     - included in index.rst, contains the content for each chapter
   * - sphinxSource/images/_.png
     - png
     - in the documentation embedded images
   * - sphinxBuild/html/index.html
     - reST
     - main file for documentation html output
   * - sphinxBuild/latex/VN-IP2-Testlab.pdf
     - pdf
     - the pdf output file.

Installation of sphinx

.. code:: sh

    sudo apt-get install python3-sphinx
    sudo pip3 --proxy http://10.182.87.94:8086 install sphinx_bootstrap_theme



* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
