#!/usr/bin/env python
#
#   Run various tests with coverage applied.
#

import coverage, doctest, sys, os, getopt
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

version_str = '%s.%s.%s' % (
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.releaselevel,
)

coverage_dir = '.coverage-results/'
opts, args = getopt.getopt(sys.argv[1:], 'cd:')
for opt, arg in opts:
    if opt == '-c':
        dump_coverage = True
    if opt == '-d':
        coverage_dir = arg

coverage_dir = os.path.join(coverage_dir, 'doctests-' + version_str)
coverage_dir = os.path.abspath(coverage_dir)
cov = coverage.coverage(data_file='.coverage-' + version_str)
cov.exclude('-nodt')
cov.start()
# TODO: Auto-discovery within bw/
rv = doctest.testfile('bw/bwconstraint.py')
cov.stop()
cov.save()
cov.html_report(directory=coverage_dir, include='bw/*')
dump = StringIO()
pct = int(0.005 + cov.report(file=dump, include='bw/*'))
if pct < 100:
    print('file://' + coverage_dir + '/index.html')
    print(dump.getvalue())
    sys.exit(1)
sys.exit(rv)
