.. _installation_generic:

Installation - Generic
========================

Dependencies
++++++++++++++

You will need to install the following software packages:

* `Oracle Java 6`_ JDK
* Python_ (tested with ver. 2.6)
* Hadoop_ (tested with version ver. 0.20)
* Ant_
* Pydoop_
* Protobuf_
* Boost_ (for Pydoop.  You'll only need the Python library)

To run the unit tests you'll also need:

* `JUnit 4`_
* ant-junit

Ant and JUnit and only build-time dependencies, so they don't need to be
installed on all your cluster nodes.  On the other hand, the rest of the
software does.  As such, you will need to either install the software to all the
nodes, or install it to a shared volume.

We recommend installing these tools/libraries as packaged by your favourite
distribution. 


Hadoop
-------

Set the environment variable ``HADOOP_HOME`` to point to your Hadoop
installation path.

The build process needs the Hadoop jars.  It expects to find them under the
``${HADOOP_HOME}/lib`` directory.

For example::

  export HADOOP_HOME=/home/user/hadoop-0.20



Building
+++++++++++

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

If however you want to build yourself a local copy, you can do so by:

#. installing Sphinx_ (see instructions below)
#. going to the Seal directory
#. running:

::

  make doc



You'll find the documentation in HTML in ``docs/_build/html/index.html``.


Installing Sphinx
....................

See if your Linux distribution includes a packaged version of Sphinx (if
probably does).  Alternatively, if you're using Python Setuptools, you can use
Easy Install::

  easy_install -U Sphinx

Finally, you can install manually by following the instructions on the Sphinx
web site:  http://sphinx.pocoo.org/.




.. _Pydoop: https://sourceforge.net/projects/pydoop/
.. _Hadoop: http://hadoop.apache.org/
.. _Python: http://www.python.org
.. _Ant: http://ant.apache.org
.. _Protobuf: http://code.google.com/p/protobuf/
.. _JUnit 4: http://www.junit.org/
.. _Oracle Java 6: http://java.com/en/download/index.jsp
.. _Sphinx:  http://sphinx.pocoo.org/
.. _Installing on Gentoo:  installation_gentoo
.. _Installing on Ubuntu:  installation_ubuntu
.. _Boost:  http://www.boost.org/