# 
# Given a topography file, this python file will create
# the inputs needed in setrun.py for a fgmax grid where pointstyle==4
# as well as the input needed for a RuledRectangle flagregion to force refinement
# around that grid.
#
# Points are selected based on the quality of being within n-points of the shoreline
#                                                   within 0-n m elevation along shoreline
#                                                   within -n-0 m depth bathymetry along shoreline
#
# Before being combined and intersected for a complete points file, structured like the input topography file
# where 1 indicates the point is in the fgmax grid, and 0 indicates the point is not included
# The RuledRectangle created can be specified by ixy='x' or ixy='y', the easiest way to tell which is 
# preferable is to make an image showing the RuledRectangle to determine if it is valid and does not waste time
# refining unnecessary domain
#


#set up environment and imported modules
import os
os.environ['CLAW'] = 'Users/anitamiddleton/Documents/python/clawpack'
os.environ['FC'] = 'gfortran'
import clawpack 

#dir = os.path.join(os.environ['CLAW'], 'geoclaw/examples/urakawa1982/scratch')
dir = '/Users/anitamiddleton/Documents/python/urakawa1982/scratch/'

# create ruled region
from clawpack.amrclaw import region_tools
from clawpack.geoclaw import topotools, marching_front
import numpy as np

topo_path = os.path.join(dir, 'cropped_hokkaido.tt3')
topo = topotools.Topography(topo_path, topo_type=3)

# qualities used to select points for the fgmax grid
pts_from_shoreline = 20
meters_elevation = 15
meters_depth = -15

# within pts_from_shoreline points of the coast
pts_chosen = marching_front.select_by_flooding(topo.Z, Z1=0, Z2=1e10, max_iters=pts_from_shoreline)
Zmasked = np.ma.masked_array(topo.Z, np.logical_not(pts_chosen))

# from 0 - meters_elevation m elevation along coast
# these points are added onto the previously chosen points
pts_chosen = marching_front.select_by_flooding(topo.Z, Z1=0, Z2=meters_elevation,
                                               prev_pts_chosen=pts_chosen,
                                               max_iters=None)

Zmasked = np.ma.masked_array(topo.Z, np.logical_not(pts_chosen))

# shallow bathymetry points, from 0 to meters_depth along coastline
pts_chosen_shallow = marching_front.select_by_flooding(topo.Z, Z1=0, Z2=meters_depth, max_iters=None)
Zshallow = np.ma.masked_array(topo.Z, np.logical_not(pts_chosen_shallow))

# intersect shallow bathymetry and coastal
pts_chosen_nearshore = np.logical_and(pts_chosen, pts_chosen_shallow)
Znearshore = np.ma.masked_array(topo.Z, np.logical_not(pts_chosen_nearshore))

# create file structured like the input topo file
fname_fgmax_mask = 'scratch/fgmax_pts_topostyle.data'
topo_fgmax_mask = topotools.Topography()
topo_fgmax_mask._x = topo.x
topo_fgmax_mask._y = topo.y
topo_fgmax_mask._Z = np.where(pts_chosen_nearshore, 1, 0)  # change boolean to 1/0
topo_fgmax_mask.generate_2d_coordinates()

# write the file to save the fgmax point data
topo_fgmax_mask.write(fname_fgmax_mask, topo_type=3, Z_format='%1i')
print('Created %s' % fname_fgmax_mask)


# create the ruled rectangle to force refinement around this fgmax grid
rr = region_tools.ruledrectangle_covering_selected_points(topo.X, topo.Y, pts_chosen_nearshore,
                                                          ixy='y', method=0,
                                                          padding=0, verbose=True)
xv,yv = rr.vertices()
rr.write('scratch/RuledRectangle_fgmax.data')

# check the structure of the RuledRectangle
if 0:
    from clawpack.visclaw import colormaps
    from clawpack.visclaw.plottools import pcolorcells
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    zmin = -100.
    zmax = 200.
    land_cmap = colormaps.make_colormap({ 0.0:[0.1,0.4,0.0],
                                        0.25:[0.0,1.0,0.0],
                                        0.5:[0.8,1.0,0.5],
                                        1.0:[0.8,0.5,0.2]})

    sea_cmap = colormaps.make_colormap({ 0.0:[0,0,1], 1.:[.8,.8,1]})
    cmap, norm = colormaps.add_colormaps((land_cmap, sea_cmap),
                                        data_limits=(zmin,zmax),
                                        data_break=0.)    

    pcolorcells(topo.X, topo.Y, Znearshore, cmap=cmap, norm=norm)
    ax.set_xlim([138, 147]) # change for different regions
    ax.set_ylim([41, 44])
    fig.gca().set_aspect(1./np.cos(48*np.pi/180.))
    ax.plot(xv, yv, 'r')
    ax.set_title("With ixy = 'y'") # or ixy='x'
    plt.show()