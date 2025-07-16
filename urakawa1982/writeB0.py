import os
from pylab import *
from clawpack.geoclaw import fgmax_tools

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

# Scratch directory for storing topo and dtopo files:
dir = '/Users/anitamiddleton/Documents/python/tsunami_proj'

outdir = os.path.join(dir, 'outputs/urakawa1982/_output')
print('Using output from outdir = ', outdir)
# Read fgmax data:
fg = fgmax_tools.FGmaxGrid()
fgmax_input_file_name = outdir + '/fgmax_grids.data'
print('fgmax input file: \n  %s' % fgmax_input_file_name)
fg.read_fgmax_grids_data(fgno=1, data_file=fgmax_input_file_name)
fg.read_output(outdir=outdir)
B0 = where(fg.B > -1e9, fg.B, -9999.)
fname = os.path.join(dir, 'scratch/urakawa1982/urakawa1982_B0.txt')
savetxt(fname, B0, fmt='%.3f')
print('saved %s' % fname)