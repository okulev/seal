# Copyright (C) 2011-2012 CRS4.
#
# This file is part of Seal.
#
# Seal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Seal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Seal.  If not, see <http://www.gnu.org/licenses/>.

"""Seal: Sequence Alignment on Hadoop.

Seal is a of MapReduce application for biological
sequence alignment. It runs on Hadoop (http://hadoop.apache.org)
through Pydoop (http://pydoop.sourceforge.net), a Python MapReduce
and HDFS API for Hadoop.
"""

import glob
import os
import shutil
import sys
from distutils.core import setup
from distutils.errors import DistutilsSetupError
from distutils.command.build import build as du_build
from distutils.command.clean import clean as du_clean

def get_arg(name):
	arg_start = "%s=" % name
	for i in xrange(len(sys.argv)):
		arg = sys.argv[i]
		if arg.startswith(arg_start):
			value = arg.replace(arg_start, "", 1)
			del sys.argv[i]
			if not value:
				raise RuntimeException("blank value specified for %s" % name)
			return value
	return None

def check_python_version():
	override = ("true" == get_arg("override_version_check"))
	if not override and sys.version_info < (2,6):
		print >>sys.stderr, "Please use a version of Python >= 2.6 (currently using vers. %s)." % ",".join( map(str, sys.version_info))
		print >>sys.stderr, "Specify setup.py override_version_check=true to override this check."
		sys.exit(1)


def get_version():
  vers = get_arg("version")
  if vers is None:
    # else, if no version specified on command line
    version_filename = os.path.join( os.path.dirname(__file__), 'VERSION')
    if os.path.exists(version_filename):
      with open(version_filename) as f:
        vers = f.read().rstrip("\n")
    else:
      from datetime import datetime
      vers = datetime.now().strftime("devel-%Y%m%d")#_%H%M%S")
  return vers

class seal_build(du_build):
  ## Add a --hadoop-bam option to our build command.
  # The only way I've found to make this work is to
  # directly add the option definition to the user_options
  # array in du_build.
  #
  # call setup.py as
  #  python setup.py build --hadoop-bam=/my/path/to/hadoop-bam
  # to make it work.
  du_build.user_options.append( ('hadoop-bam=', None, "Path to directory containing Hadoop-BAM jars" ) )

  def initialize_options(self):
    du_build.initialize_options(self)
    self.hadoop_bam = None

  def finalize_options(self):
    du_build.finalize_options(self)
    # HACK!  Use a global variable until we find a better way to
    # pass a parameter into the build command.
    global VERSION
    self.version = VERSION
    # BUG:  get_arg("override_version_check") doesn't work here
    # since the argument has already been eaten by check_python_version(),
    # called before setup
    self.override_version_check = get_arg("override_version_check") or 'false'
    # look for HadoopBam, if it hasn't been provided as a command line argument
    if self.hadoop_bam is None:
      # check environment variable HADOOP_BAM
      self.hadoop_bam = os.environ.get("HADOOP_BAM", None)
      # else assume they'll be somewhere in the class path (e.g. Hadoop directory)
    if self.hadoop_bam:
      print >>sys.stderr, "Using hadoop-bam in", self.hadoop_bam
    else:
      print >>sys.stderr, "Hadoop-BAM path not specified.  Trying to build anyways."
      print >>sys.stderr, "You can specify a path with:"
      print >>sys.stderr, "python setup.py build --hadoop-bam=/my/path/to/hadoop-bam"
      print >>sys.stderr, "or by setting the HADOOP_BAM environment variable."
 
  def run(self):
    # Create (or overwrite) seal/version.py
    with open(os.path.join('seal', 'version.py'), 'w') as f:
      f.write('version = "%s"' % self.version)

    # run the usual build
    du_build.run(self)

    # make bwa
    libbwa_dir = "seal/lib/aligner/bwa"
    libbwa_src = os.path.join(libbwa_dir, "libbwa")
    libbwa_dest = os.path.abspath(os.path.join(self.build_purelib, libbwa_dir))
    ret = os.system("BWA_LIBRARY_DIR=%s make -C %s libbwa" %
                    (libbwa_dest, libbwa_src))
    if ret:
      raise DistutilsSetupError("could not make libbwa")

    # protobuf classes
    proto_src = "seal/lib/io/mapping.proto"
    ret = os.system("protoc %s --python_out=%s" %
                    (proto_src, self.build_purelib))
    if ret:
      raise DistutilsSetupError("could not run protoc")

    # Java stuff
    ant_cmd = 'ant -Dversion="%s" -Doverride_version_check="%s"' % (self.version, self.override_version_check)
    if self.hadoop_bam:
      ant_cmd += ' -Dhadoop.bam="%s"' % self.hadoop_bam
    ret = os.system(ant_cmd)
    if ret:
      raise DistutilsSetupError("Could not build Java components")
    # finally make the jar
    self.package()

  def package(self):
    dest_jar_path = os.path.join(self.build_purelib,'seal', 'seal.jar')
    if os.path.exists(dest_jar_path):
      os.remove(dest_jar_path)
    shutil.move( os.path.join(self.build_base, 'seal.jar'), dest_jar_path )

# Custom clean action that removes files generated by the build process.
class seal_clean(du_clean):
  def run(self):
    du_clean.run(self)
    os.system("make -C docs clean")
    os.system("ant clean")
    os.system("rm -f seal/lib/aligner/bwa/libbwa/bwa")
    os.system("rm -f seal/version.py")
    os.system("rm -rf dist MANIFEST")

    os.system("find seal bin -name '*.pyc' -print0 | xargs -0  rm -f")
    os.system("find seal/lib/aligner/bwa/libbwa/ \( -name '*.ol' -o -name '*.o' -o -name '*.so' \) -print0 | xargs -0  rm -f")
    os.system("find . -name '*~' -print0 | xargs -0  rm -f")


#############################################################################
# main
#############################################################################

# chdir to Seal's root directory (where this file is located)
os.chdir(os.path.abspath(os.path.dirname(__file__)))

check_python_version()

NAME = 'seal'
DESCRIPTION = __doc__.split("\n", 1)[0]
LONG_DESCRIPTION = __doc__
URL = "http://www.crs4.it"
# DOWNLOAD_URL = ""
LICENSE = 'GPL'
CLASSIFIERS = [
  "Programming Language :: Python",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  "Operating System :: POSIX :: Linux",
  "Topic :: Scientific/Engineering :: Bio-Informatics",
  "Intended Audience :: Science/Research",
  ]
PLATFORMS = ["Linux"]
VERSION = get_version()
AUTHOR_INFO = [
  ("Luca Pireddu", "luca.pireddu@crs4.it"),
  ("Simone Leo", "simone.leo@crs4.it"),
  ("Gianluigi Zanetti", "gianluigi.zanetti@crs4.it"),
  ]
MAINTAINER_INFO = [
  ("Luca Pireddu", "luca.pireddu@crs4.it"),
  ]
AUTHOR = ", ".join(t[0] for t in AUTHOR_INFO)
AUTHOR_EMAIL = ", ".join("<%s>" % t[1] for t in AUTHOR_INFO)
MAINTAINER = ", ".join(t[0] for t in MAINTAINER_INFO)
MAINTAINER_EMAIL = ", ".join("<%s>" % t[1] for t in MAINTAINER_INFO)


setup(name=NAME,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      url=URL,
##      download_url=DOWNLOAD_URL,
      license=LICENSE,
      classifiers=CLASSIFIERS,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      platforms=PLATFORMS,
      version=VERSION,
      packages=['seal',
                'seal.lib',
                'seal.lib.aligner',
                'seal.lib.aligner.bwa',
                'seal.lib.io',
                'seal.lib.mr',
                'seal.seqal',
                ],
      cmdclass={"build": seal_build, "clean": seal_clean},
      scripts=glob.glob("bin/*"),
      )
