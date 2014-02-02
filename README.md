bullwinkle
==========

Python OO extensions (very) loosely based on Perl's Moose.

Installation
============

On the shell:

    pip install -r requirements.txt

Developer Setup
===============

On the shell:

    virtualenv -p python2 ve2
    virtualenv -p python3 ve3
    pip install -r requirements.txt
    pip install -r devel-requirements.txt

Now create two windows/screens/terms.  On one:

    . ve2/bin/activate
    ./rerun.sh ./test_all.sh

In the other:

    . ve3/bin/activate
    ./rerun.sh ./test_all.sh


