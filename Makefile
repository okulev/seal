
DOCS_SRC := docs
DOCS := $(DOCS_SRC)/_build/html
BuildDir := build
JAR := $(BuildDir)/seal.jar

# If a VERSION file is available, the version name is take from there.
# Else a development version number is made from the current timestamp
version := $(shell cat VERSION 2>/dev/null || date "+devel-%Y%m%d_%H%M%S")

SealName := seal-$(version)
SealBaseDir := $(BuildDir)/$(SealName)
Tarball := $(BuildDir)/$(SealName).tar.gz

.PHONY: clean distclean

all: dist
	
dist: $(Tarball)

$(Tarball): jbuild pbuild
	rm -rf "$(SealBaseDir)"
	mkdir $(SealBaseDir) "$(SealBaseDir)/bin"
	ln $(JAR) $(SealBaseDir)/seal.jar
	ln bin/* $(SealBaseDir)/bin
	cp -r $(BuildDir)/bl $(SealBaseDir)/bl
	cp $(BuildDir)/*.egg-info $(SealBaseDir)/
	tar -C $(BuildDir) -czf $(Tarball) $(SealName)

jbuild: $(JAR)

$(JAR): build.xml src
	ant -Dversion="${version}"

pbuild: bl
	python setup.py install --install-lib $(BuildDir) version="${version}"

doc: $(DOCS)

$(DOCS): $(DOCS_SRC)
	make -C $< html

upload-docs: doc
	rsync -avz --delete -e ssh --exclude=.buildinfo docs/_build/html/ ilveroluca,biodoop-seal@web.sourceforge.net:/home/project-web/biodoop-seal/htdocs

clean:
	ant clean
	rm -rf build
	make -C docs clean
	rmdir docs/_build docs/_templates docs/_static || true
	find bl -name '*.pyc' -print0 | xargs -0  rm -f
	find bl/lib/seq/aligner/bwa/libbwa/ -name '*.ol' -o -name '*.o' -print0 | xargs -0  rm -f
	rm -f bl/lib/seq/aligner/bwa/libbwa/bwa
	find . -name '*~' -print0 | xargs -0  rm -f

distclean: clean
