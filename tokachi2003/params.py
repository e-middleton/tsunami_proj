"""
Parameters specific to the earthquake source (and the location).
"""

import os

# topography directory

# root_dir = '~/Documents/python/tsunami_proj'
# topo_dir = 'scratch/common_topo'

# point this environment variable to wherever clawpack has been cloned / installed on your computer
os.environ['CLAW'] = '/Users/anitamiddleton/Documents/python/clawpack'

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

root_dir = '/Users/anitamiddleton/Documents/python/tsunami_proj'
scratch_dir = os.path.join(root_dir, 'scratch')

# ADJUST
which_test = input("Which test in the scratch directory from this project would you like to run? ")
test_dir = os.path.join(scratch_dir, 'tokachi2003', which_test)


makeB0 = False

amr_max = 5

num_output_times = 48
end_time = 4*3600.

# computational domain
lower = [138.0, 38]
upper = [148.0, 46]

# coarsest grid [x,y]
# 2 degrees resolution
num_cells = [5, 4]
regions = []

from clawpack.geoclaw import fgmax_tools
from clawpack.amrclaw.data import FlagRegion

## REGIONS ##

flagregions = []

regions = []
# to specify regions of refinement append lines of the form
#  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
inf = 1e9 

x1,x2,y1,y2 = lower[0], upper[0], lower[1], upper[1]

flagregion = FlagRegion(num_dim=2)  # so far only 2D supported
flagregion.name = 'Region_domain'
flagregion.minlevel = 1
flagregion.maxlevel = amr_max-1
flagregion.t1 = 0.
flagregion.t2 = 1e9
flagregion.spatial_region_type = 1  # Rectangle
flagregion.spatial_region = [x1,x2,y1,y2]
flagregions.append(flagregion)

# fgmax grid covers all areas of interest
flagregion2 = FlagRegion(num_dim=2)
flagregion2.name = 'Region_FGMax_points'
flagregion2.minlevel = amr_max
flagregion2.maxlevel = amr_max
flagregion2.t1 = 0.
flagregion2.t2 = 1e9
flagregion2.spatial_region_type = 2  # Ruled Rectangle
flagregion2.spatial_region_file = \
    os.path.join(scratch_dir, 'tokachi2003/RuledRectangle_fgmax.txt')
flagregions.append(flagregion2)


## FGMax grids ##

## Fixed grid monitoring ##
from clawpack.geoclaw import fgmax_tools

num_fgmax_val = 1 # to save only depth (2 saves depth and speed)
fgmax_grids = []  # empty list to start


# Now append to this list objects of class fgmax_tools.FGmaxGrid
# specifying any fgmax grids.

# Points on a uniform 2d grid:
fg = fgmax_tools.FGmaxGrid()
fg.fgno = 1
# fgmax grid point_style==4 means grid specified as topo_type==3 file:
fg.point_style = 4
fg.xy_fname = os.path.join(scratch_dir, 'tokachi2003/fgmax_pts_topostyle.txt')  # file of 0/1 values in tt3 format
fg.tstart_max = 5. # after rupture (hopefully)
fg.tend_max = end_time # same as final time for whole run
fg.dt_check = 0 # monitor every time step
fg.min_level_check = amr_max
fgmax_grids=[fg]



# ---------------
# Gauges:
# ---------------
gauges = []
# # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
gauges.append([129, 142.765722, 42.166085, 0., 1.e10]) # urakawa
gauges.append([111, 143.324564, 42.293637, 0., 1.e10]) # tokachi ko
gauges.append([112, 144.37100220, 42.87560120, 0., 1.e10]) # Kushiro



# topography
topofiles = []

topo_path = os.path.join(scratch_dir, 'curr_topo.tt3')
topofiles.append([3, topo_path])


# dtopo files 
# if makeB0 is set to true, no deformation is used in the geoclaw run
# so the original values of topography can be saved for the fgmax grid
if makeB0==False:
    dtopo_path = os.path.join(test_dir, 'dtopo.tt3')
    print(dtopo_path)
    dtopofiles = [[3,dtopo_path]]
else:
    dtopofiles=[]
