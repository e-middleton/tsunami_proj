
from __future__ import absolute_import
from __future__ import print_function
import os
from pylab import *
from clawpack.geoclaw import fgmax_tools

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

# Scratch directory for storing topo and dtopo files:
#dir = os.path.join(CLAW, 'geoclaw/examples/urakawa1982')
dir = '/Users/anitamiddleton/Documents/python/urakawa1982'

locs = ['Hokkaido']

#locs = ['Discovery_PT']  # to process a single LOC

for loc in locs:
    outdir = os.path.join(dir, '_output')
    print('Using output from outdir = ', outdir)
    # Read fgmax data:
    fg = fgmax_tools.FGmaxGrid()
    fgmax_input_file_name = os.path.join(dir, 'fgmax_grids.data')
    print('fgmax input file: \n  %s' % fgmax_input_file_name)
    fg.read_fgmax_grids_data(fgno=1, data_file=fgmax_input_file_name)
    fg.read_output(outdir=outdir)
    B0 = where(fg.B > -1e9, fg.B, -9999.)
    fname = '%s_B0.txt' % loc
    savetxt(fname, B0, fmt='%.3f')
    print('saved %s, move to input_files' % fname)