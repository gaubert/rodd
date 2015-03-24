#=============================================================================
# File: Simple Makefile for Dissemination Monitoring Toolbox
# author: guillaume.aubert@eumetsat.int
#=============================================================================
BASEDIR=.
# internal dirs
DISTS=$(BASEDIR)/dists

#DissTBDist
DTBDIST=$(DISTS)/disstoolbox-dist
DTBBUILD=$(DTBDIST)/build
DTBBUILDDIST=$(DTBDIST)/build/egg-dist

#DPlayDist
DPLDIST=$(DISTS)/dissplayer-dist
DPLBUILD=$(DPLDIST)/build
DPLBUILDDIST=$(DPLDIST)/build/egg-dist

#ConfDist info
CONFDIST=$(DISTS)/conf-dist
CONFBUILD=$(CONFDIST)/build
CONFBUILDDIST=$(CONFDIST)/build

BUILD=$(BASEDIR)/build
BUILDDIST=$(BUILD)/egg-dist
ETC=$(BASEDIR)/etc

#PYTHONBIN=/homespace/gaubert/python2.7/bin/python
PYTHONBIN=/drives/c/GuillaumeAubertSpecifics/Programs/WinPython-32bit-2.7.6.4/python-2.7.6/python.exe
PYTHONVERSION=2.7

# new version 1.3.3.2 released 270410 

DTBVERSION=0.3
DTBDISTNAME=diss-toolbox-$(DTBVERSION)

all: dissplayer-src-dist

init:
	mkdir -p $(DTBDIST)
	mkdir -p $(DTBBUILDDIST)
	mkdir -p $(DPLDIST)
	mkdir -p $(DPLBUILDDIST) 

#this is the one we use at the moment
# to install with pip: /tmp/python-test/bin/pip install ./dmon-0.5.tar.gz --find-links file:///homespace/gaubert/Dev/projects/rodd/dists/disstoolbox-dist/third-party
disstoolbox-src-dist: clean init
	# need to copy sources in distributions as distutils does not always support symbolic links (pity)
	mkdir -p $(DTBDIST)/eumetsat
	cp $(BASEDIR)/src/eumetsat/__init__.py $(DTBDIST)/eumetsat	
	cp -R $(BASEDIR)/src/eumetsat/dmon $(DTBDIST)/eumetsat
	cd $(DTBDIST); $(PYTHONBIN) setup.py sdist -d ../../$(DTBBUILD) 
	#remove egg-dist dir
	rm -Rf $(DTBBUILD)/egg-dist
	#copy third party libs in build dir in order to create one tarball that can be installed with pip
	cp $(DTBDIST)/third-party/* $(DTBBUILD)
	echo "distribution stored in $(DTBBUILD)"

# to install with pip: /tmp/python-test/bin/pip install ./dmon-0.5.tar.gz --find-links file:///homespace/gaubert/Dev/projects/rodd/dists/disstoolbox-dist/third-party
dissplayer-src-dist: clean init
	# need to copy sources in distributions as distutils does not always support symbolic links (pity)
	mkdir -p $(DPLDIST)/eumetsat
	# copy script
	cp -R $(BASEDIR)/etc/diss-player $(DPLDIST)
	# dos2unix it
	dos2unix $(DPLDIST)/diss-player/diss-player
	cp -R $(BASEDIR)/src/eumetsat/__init__.py $(DPLDIST)/eumetsat
	cp -R $(BASEDIR)/src/eumetsat/dmon $(DPLDIST)/eumetsat
	cd $(DPLDIST); $(PYTHONBIN) setup.py sdist -d ../../$(DPLDIST)
	#remove egg-dist dir
	rm -Rf $(DPLDIST)/egg-dist
	#copy third party libs in build dir in order to create one tarball that can be installed with pip
	cp $(DPLDIST)/third-party/* $(DPLBUILD)
	echo "distribution stored in $(DPLBUILD)"

disstoolbox-src-egg-dist: clean init
	# need to copy sources in distributions as distutils does not always support symbolic links (pity)
	mkdir -p $(DTBDIST)/eumetsat
	cp $(BASEDIR)/src/eumetsat/__init__.py $(DTBDIST)/eumetsat	
	mkdir -p $(DTBBUILDDIST)
	cp -R $(BASEDIR)/src/eumetsat $(DTBDIST)
	echo "distribution stored in $(DTBBUILD)"
    
disstoolbox-egg-dist: init 
	cp -R $(BASEDIR)/src/eumetsat/dmon $(DTBDIST)
	cd $(DTBDIST); $(PYTHONBIN) setup.py bdist_egg -b /tmp/build -p $(DTBDISTNAME) -d ../../$(DTBBUILDDIST) 
	echo "distribution stored in $(DTBBUILDDIST)"

clean: clean-build
	cd $(DTBDIST); rm -Rf build; rm -Rf *.egg-info; rm -Rf dist; rm -Rf eumetsat
	cd $(DPLDIST); rm -Rf build; rm -Rf *.egg-info; rm -Rf dist; rm -Rf eumetsat
	
clean-build:
	cd $(DTBBUILD); rm -Rf egg-dist; 
	rm -Rf $(DTBDIST)/diss-toolbox-*
	cd $(DTBBUILD); rm -Rf egg-dist
	rm -Rf $(DPLBUILD)/*;
	rm -Rf $(DPLDIST)/eumetsat
    


