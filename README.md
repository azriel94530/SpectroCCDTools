# SpectroCCDTools
This directory contains a bunch of tools for reconstructing, manipulating, and analyzing, FITS
images from the SpectroCCD.  For now, everything runs in python, with calls to the packages:
- time
- sys
- os
- numpy
- astropy.io.fits
- ROOT

All but the last two are part of most stock system python distributions. The easiest way to get 
"astropy.io.fits" is to download anaconda (https://store.continuum.io/cshop/anaconda/), which you
should probably do anyway since it's the best way to get a bunch of useful libraries.  

ROOT is an analysis packge that comes out of CERN and the rest of the high-energy physics 
community.  It can be found at https://root.cern.ch.  We are of course using the python bindings 
for ROOT.  When using root with anaconda, there are a couple of tricks one has to play. First, 
always make sure you have installed anaconda BEFORE you build ROOT so that the python libraries 
all agree with one another, regardless of platform.  Building ROOT can seem a little daunting, but
is not so bad once you see how it works. Download the source tar ball, and unpack it.  The move the
source directory to someplace you want it to live.  I like /usr/local/root.

* Linux:
Run the configure script from the command line with a:
[prompt] sudo ./configure linuxx8664gcc --enable-python --enable-roofit
* Mac:
Run the configure script from the command line with a:
[prompt] sudo ./configure macosx64 --enable-cocoa --enable-python --with-python-libdir=/Users/vmgehman/anaconda/lib/ --with-python-incdir=/Users/vmgehman/anaconda/include --enable-roofit

* Either
Once the configure script finshes, build ROOT with a:
[prompt] sudo make -jN
where N is the number of parallel build jobs you want to launch.  This should be less than or equal 
to the number of cores in whatever machine you are using.

The build will take between ten minutes and about an hour depending on how fast and how
parallelized your computer is.  Once that's done, you need to add the following line to your 
.bashrc (linux) or .bash_profile (mac):
source /usr/local/root/bin/thisroot.sh
This will run the root setup script whenever you open a terminal prompt.  I also like to add:
alias root='root -l'
because this gets rid of the ROOT splash screen when you start it, which can be a little annoying.

On linux, you're ready to go.  On a mac, you still have to make sure that python and ROOT know 
about each other with a:
[prompt] sudo install_name_tool -change libpython2.7.dylib /path/to/anaconda/lib/libpython2.7.dylib /path/to/root/lib/libPyROOT.so

At this point, you should be ready to go!  One word of caution: there seems to be some destructive 
interference between astropy.io.fits and ROOT.  I get errors when opening FITS images if I do so 
after importing ROOT.  This is fine as long as you wait to do your "import ROOT" until after you 
have read in all the FITS image you need.  I am exploring some options for how to deal with this 
more gracefully.

Vic Gehman (vmgehman@lbl.gov)
04/30/2015