.. _installation_ubuntu:

Installation - Ubuntu
=======================


Install Dependencies
++++++++++++++++++++++

You'll need to activate the "partner" repositories in
``/etc/apt/sources.list`` by uncommenting the lines below::

  deb http://archive.canonical.com/ubuntu maverick partner
  deb-src http://archive.canonical.com/ubuntu maverick partner

Substitute ``maverick`` with your Ubuntu release name.
These sources are required for the Java package.


Now update your package list and install all the required packages::

  sudo apt-get update

  sudo apt-get install sun-java6-jdk python protobuf-compiler \
  libprotobuf6 libprotoc6 python-protobuf ant ant-optional g++ \
  libboost-python-dev

Ant and JUnit and only build-time dependencies, so they don't need to be
installed on all your cluster nodes.  On the other hand, the rest of the
software does.  As such, you will need to either install the software to all the
nodes, or install it to a shared volume.


Install Hadoop
+++++++++++++++++

If you haven't done so already, set up your Hadoop cluster.  Please refer to 
the Hadoop documentation for your chosen distribution:

* `Instructions for Apache Hadoop <http://hadoop.apache.org/common/docs/r0.20.2/cluster_setup.html>`_
* `Instructions for Cloudera Hadoop <https://ccp.cloudera.com/display/CDHDOC/CDH3+Installation>`_

Seal has been developed with Apache Hadoop 0.20, but we have also tested it
with Cloudera CDH3.


Build Pydoop
++++++++++++++++

With Tarball distributions of Hadoop (Apache and Cloudera)
------------------------------------------------------------


Download the latest version of Pydoop from here:  http://sourceforge.net/projects/pydoop/files/.
Set the ``HADOOP_HOME`` environment variable so that it points to where the
Hadoop tarball was extracted::

  export HADOOP_HOME=<path to Hadoop directory>

Then, in the same shell::

  tar xzf pydoop-0.4.0_rc2.tar.gz
  cd pydoop-0.4.0_rc2
  python setup.py build



With Packaged distributions of Cloudera Hadoop
--------------------------------------------------

Download the latest version of Pydoop from here:  http://sourceforge.net/projects/pydoop/files/.
We assume the Cloudera package repository is already in your sources (see 
`Installing CDH3 on Ubuntu Systems`_). You'll need to install the Hadoop source 
code and libhdfs::


  sudo apt-get install hadoop-source libhdfs0 libhdfs0-dev

Now extract and build Pydoop::

  tar xzf pydoop-0.4.0_rc2.tar.gz
  cd pydoop-0.4.0_rc2
  python setup.py build


Install Pydoop
++++++++++++++++

You need to decide where to install Pydoop.  Remember that it needs to be accessible by
all the cluster nodes running Seal tasks.  We recommend installing to a shared
volume, except for medium-large clusters (more than 100 nodes) where local
installation may be necessary.

If your user's home directory is accessible on all cluster nodes, then
installing it there may be a good idea::

  python setup.py install --user

Otherwise, to install to a specific path::

  python setup.py install --home <path>

For a system-wide (local) installation::

  sudo python setup.py install --skip-build

.. note::
  If you had to export HADOOP_HOME to build Pydoop, make sure the variable is also set when you call ``setup.py install``.
  The `Pydoop documentation <http://pydoop.sourceforge.net/docs/>`_ has more details regarding its installation.



Build Seal
++++++++++++++


Seal needs the Hadoop jars to compile.  Tell the build script where to find them
by setting the ``HADOOP_HOME`` environment variable.

If you installed Hadoop from a tarball, set ``HADOOP_HOME`` to point to the
extracted copy of the archive.  For instance::

  export HADOOP_HOME=/home/me/hadoop-0.20

If you installed Hadoop from the Cloudera packages, set ``HADOOP_HOME`` like
this::

  export HADOOP_HOME=/usr/lib/hadoop


The build process expects to find the Hadoop jars in the
``${HADOOP_HOME}`` and ``${HADOOP_HOME}/lib`` directories.


Seal includes Java, Python and C components that need to be built.  A Makefile 
is provided that builds all components.  Simply go into the root Seal source
directory and run::

  make

This will create the archive ``build/seal.tar.gz`` containing all Seal
components.  Inside ``build`` you'll also find the individual components:

* ``seal.jar``;
* ``lib`` directory, containing Python modules.


Creating the documentation
----------------------------

You can find the documentation for Seal at http://biodoop-seal.sourceforge.net/.

If however you want to build yourself a local copy, you can do so in three steps:

#. install Sphinx_: ``sudo apt-get install python-sphinx``
#. go to the Seal directory
#. run: ``make doc``


You'll find the documentation in HTML in ``docs/_build/html/index.html``.


.. _Pydoop: https://sourceforge.net/projects/pydoop/
.. _Hadoop: http://hadoop.apache.org/
.. _Python: http://www.python.org
.. _Ant: http://ant.apache.org
.. _Protobuf: http://code.google.com/p/protobuf/
.. _JUnit 4: http://www.junit.org/
.. _distutils: http://docs.python.org/install/index.html
.. _Oracle Java 6: http://java.com/en/download/index.jsp
.. _Sphinx:  http://sphinx.pocoo.org/
.. _Installing on Gentoo:  installation_gentoo
.. _Installing on Ubuntu:  installation_ubuntu
.. _Installing CDH3 on Ubuntu Systems: https://ccp.cloudera.com/display/CDHDOC/CDH3+Installation#CDH3Installation-InstallingCDH3onUbuntuSystems