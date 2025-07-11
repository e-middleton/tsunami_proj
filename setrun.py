"""
Module to set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.

"""

from __future__ import absolute_import
from __future__ import print_function
import os
import numpy as np

os.environ["CLAW"] = '/Users/anitamiddleton/Documents/python/clawpack'

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

# Scratch directory for storing topo and dtopo files:
#dir = os.path.join(CLAW, 'geoclaw/examples/urakawa1982/scratch')
dir = '/Users/anitamiddleton/Documents/urakawa1982/scratch'


#------------------------------
def setrun(claw_pkg='geoclaw'):
#------------------------------

    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    from clawpack.clawutil import data

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = data.ClawRunData(claw_pkg, num_dim)


    #------------------------------------------------------------------
    # Problem-specific parameters to be written to setprob.data:
    #------------------------------------------------------------------
    
    #probdata = rundata.new_UserData(name='probdata',fname='setprob.data')


    #------------------------------------------------------------------
    # GeoClaw specific parameters:
    #------------------------------------------------------------------
    rundata = setgeo(rundata)

    #------------------------------------------------------------------
    # Standard Clawpack parameters to be written to claw.data:
    #   (or to amr2ez.data for AMR)
    #------------------------------------------------------------------
    clawdata = rundata.clawdata  # initialized when rundata instantiated


    # Set single grid parameters first.
    # See below for AMR parameters.


    # ---------------
    # Spatial domain:
    # ---------------

    # Number of space dimensions:
    clawdata.num_dim = num_dim

    # Lower and upper edge of computational domain:
    clawdata.lower[0] = 138.0      
    clawdata.upper[0] = 148.0      

    clawdata.lower[1] = 38         
    clawdata.upper[1] = 46       
    

    # Number of grid cells: Coarsest grid
    # 2 degree resolution
    clawdata.num_cells[0] = 5 # mx
    clawdata.num_cells[1] = 4 # my

    # ---------------
    # Size of system:
    # ---------------

    # Number of equations in the system:
    clawdata.num_eqn = 3

    # Number of auxiliary variables in the aux array (initialized in setaux)
    clawdata.num_aux = 3

    # Index of aux array corresponding to capacity function, if there is one:
    clawdata.capa_index = 2

    
    
    # -------------
    # Initial time:
    # -------------

    clawdata.t0 = 0.0


    # Restart from checkpoint file of a previous run?
    # If restarting, t0 above should be from original run, and the
    # restart_file 'fort.chkNNNNN' specified below should be in 
    # the OUTDIR indicated in Makefile.

    clawdata.restart = False              # True to restart from prior results
    clawdata.restart_file = 'fort.chk00096'  # File to use for restart data

# -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 1

    if clawdata.output_style==1:
        # Output nout frames at equally spaced times up to tfinal:
        clawdata.num_output_times = 24 # every 10 minute for the first 4 hours
        clawdata.tfinal = 2*3600.
        clawdata.output_t0 = True  # output at initial (or restart) time?

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        clawdata.output_times = [0., 514.28571429]

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 3
        clawdata.output_t0 = True



    # ---------------------------------------------------
    # Verbosity of messages to screen during integration:
    # ---------------------------------------------------

    # The current t, dt, and cfl will be printed every time step
    # at AMR levels <= verbosity.  Set verbosity = 0 for no printing.
    #   (E.g. verbosity == 2 means print only on levels 1 and 2.)
    clawdata.verbosity = 1



    # --------------
    # Time stepping:
    # --------------

    # if dt_variable==1: variable time steps used based on cfl_desired,
    # if dt_variable==0: fixed time steps dt = dt_initial will always be used.
    clawdata.dt_variable = True

    # Initial time step for variable dt.
    # If dt_variable==0 then dt=dt_initial for all steps:
    clawdata.dt_initial = 0.0016

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.75
    clawdata.cfl_max = 1.0

    # Maximum number of time steps to allow between output times:
    clawdata.steps_max = 5000




    # ------------------
    # Method to be used:
    # ------------------

    # Order of accuracy:  1 => Godunov,  2 => Lax-Wendroff plus limiters
    clawdata.order = 2
    
    # Use dimensional splitting? (not yet available for AMR)
    clawdata.dimensional_split = 'unsplit'
    
    # For unsplit method, transverse_waves can be 
    #  0 or 'none'      ==> donor cell (only normal solver used)
    #  1 or 'increment' ==> corner transport of waves
    #  2 or 'all'       ==> corner transport of 2nd order corrections too
    clawdata.transverse_waves = 2

    # Number of waves in the Riemann solution:
    clawdata.num_waves = 3
    
    # List of limiters to use for each wave family:  
    # Required:  len(limiter) == num_waves
    # Some options:
    #   0 or 'none'     ==> no limiter (Lax-Wendroff)
    #   1 or 'minmod'   ==> minmod
    #   2 or 'superbee' ==> superbee
    #   3 or 'mc'       ==> MC limiter
    #   4 or 'vanleer'  ==> van Leer
    clawdata.limiter = ['mc', 'mc', 'mc']

    clawdata.use_fwaves = True    # True ==> use f-wave version of algorithms
    
    # Source terms splitting:
    #   src_split == 0 or 'none'    ==> no source term (src routine never called)
    #   src_split == 1 or 'godunov' ==> Godunov (1st order) splitting used, 
    #   src_split == 2 or 'strang'  ==> Strang (2nd order) splitting used,  not recommended.
    clawdata.source_split = 'godunov'


    # --------------------
    # Boundary conditions:
    # --------------------

    # Number of ghost cells (usually 2)
    clawdata.num_ghost = 2

    # Choice of BCs at xlower and xupper:
    #   0 => user specified (must modify bcN.f to use this option)
    #   1 => extrapolation (non-reflecting outflow)
    #   2 => periodic (must specify this at both boundaries)
    #   3 => solid wall for systems where q(2) is normal velocity

    clawdata.bc_lower[0] = 'extrap'
    clawdata.bc_upper[0] = 'extrap'

    clawdata.bc_lower[1] = 'extrap'
    clawdata.bc_upper[1] = 'extrap'



    # --------------
    # Checkpointing:
    # --------------

    # Specify when checkpoint files should be created that can be
    # used to restart a computation.

    clawdata.checkpt_style = 0

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif np.abs(clawdata.checkpt_style) == 1:
        # Checkpoint only at tfinal.
        pass

    elif np.abs(clawdata.checkpt_style) == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = [0.1,0.15]

    elif np.abs(clawdata.checkpt_style) == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5

    elif np.abs(clawdata.checkpt_style) == 4:
        # option means checkpt at same time as valout
        pass


    # ---------------
    # AMR parameters:
    # ---------------
    amrdata = rundata.amrdata

    # maximum size of patches in each direction (matters in parallel):
    amrdata.max1d = 60

    # max number of refinement levels:
    amrdata.amr_levels_max = 5

    # List of refinement ratios at each level (length at least mxnest-1)
    # 2 degree, 24', 4', 1', 10", 1"
    amrdata.refinement_ratios_x = [5, 6, 4, 6, 10]
    amrdata.refinement_ratios_y = [5, 6, 4, 6, 10]
    amrdata.refinement_ratios_t = [5, 6, 4, 6, 10]

    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center','capacity','yleft']


    # Flag using refinement routine flag2refine rather than richardson error
    amrdata.flag_richardson = False    # use Richardson?
    amrdata.flag_richardson_tol = 0.002  # Richardson tolerance
    amrdata.flag2refine = True

    # steps to take on each level L between regriddings of level L+1:
    amrdata.regrid_interval = 3

    # width of buffer zone around flagged points:
    # (typically the same as regrid_interval so waves don't escape):
    amrdata.regrid_buffer_width  = 2

    # clustering alg. cutoff for (# flagged pts) / (total # of cells refined)
    # (closer to 1.0 => more small grids may be needed to cover flagged cells)
    amrdata.clustering_cutoff = 0.700000

    # print info about each regridding up to this level:
    amrdata.verbosity_regrid = 0  

    #  ----- For developers ----- 
    # Toggle debugging print statements:
    amrdata.dprint = False      # print domain flags
    amrdata.eprint = False      # print err est flags
    amrdata.edebug = False      # even more err est flags
    amrdata.gprint = False      # grid bisection/clustering
    amrdata.nprint = False      # proper nesting output
    amrdata.pprint = False      # proj. of tagged points
    amrdata.rprint = False      # print regridding summary
    amrdata.sprint = False      # space/memory output
    amrdata.tprint = True       # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    # ---------------
    # Regions:
    # ---------------
    rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    inf = 1e9 

    from clawpack.amrclaw.data import FlagRegion
    x1,x2,y1,y2 = [rundata.clawdata.lower[0], rundata.clawdata.upper[0],
               rundata.clawdata.lower[1], rundata.clawdata.upper[1]]
    flagregion = FlagRegion(num_dim=2)  # so far only 2D supported
    flagregion.name = 'Region_domain'
    flagregion.minlevel = 1
    flagregion.maxlevel = 4
    flagregion.t1 = 0.
    flagregion.t2 = 1e9
    flagregion.spatial_region_type = 1  # Rectangle
    flagregion.spatial_region = [x1,x2,y1,y2]
    rundata.flagregiondata.flagregions.append(flagregion)

    flagregion2 = FlagRegion(num_dim=2)
    flagregion2.name = 'Region_FGMax_points'
    flagregion2.minlevel = 4
    flagregion2.maxlevel = 5
    flagregion2.t1 = 0.
    flagregion2.t2 = 1e9
    flagregion2.spatial_region_type = 2  # Ruled Rectangle
    flagregion2.spatial_region_file = \
        os.path.join(dir, 'RuledRectangle_fgmax.data')
    rundata.flagregiondata.flagregions.append(flagregion2)

    flagregion3 = FlagRegion(num_dim=2)
    flagregion3.name = "Region_fault_slip"
    flagregion3.minlevel=3
    flagregion3.maxlevel=3
    flagregion3.t1 = 0.
    flagregion3.t2 = 3600.
    flagregion3.spatial_region_type = 1 # Rectangle
    flagregion3.spatial_region = [141, 144, 40, 43]
    rundata.flagregiondata.flagregions.append(flagregion3)

    flagregion4 = FlagRegion(num_dim=2)
    flagregion4.name = "Region_urakawa_gauge"
    flagregion4.minlevel=4
    flagregion4.maxlevel=5
    flagregion4.t1 = 0.
    flagregion4.t2 = inf
    flagregion4.spatial_region_type=1
    flagregion4.spatial_region = [142.6, 142.85, 41.9, 42.3]
    rundata.flagregiondata.flagregions.append(flagregion4)

    flagregion5 = FlagRegion(num_dim=2)
    flagregion5.name = "Region_erimo_port"
    flagregion5.minlevel=4
    flagregion5.maxlevel=5
    flagregion5.t1 = 0.
    flagregion5.t2 = inf
    flagregion5.spatial_region_type=1
    flagregion5.spatial_region=[143, 143.3, 41.9, 42.2]
    rundata.flagregiondata.flagregions.append(flagregion5)

    flagregion6 = FlagRegion(num_dim=2)
    flagregion6.name = "Region_tomakomai_port"
    flagregion6.minlevel = 4
    flagregion6.maxlevel = 5
    flagregion6.t1 = 0.
    flagregion6.t2 = inf
    flagregion6.spatial_region_type=1
    flagregion6.spatial_region=[141, 142, 42, 43]
    rundata.flagregiondata.flagregions.append(flagregion6)

   # ---------------
    # Gauges:
    # ---------------
    rundata.gaugedata.gauges = []
    # # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    rundata.gaugedata.gauges.append([129, 142.765722, 42.166085, 0., 1.e10]) # urakawa
    rundata.gaugedata.gauges.append([112, 143.135422, 42.010444, 0., 1e10]) # erimo port location
    rundata.gaugedata.gauges.append([113, 141.613420, 42.614828, 0., 1e10]) # tomakomai (outside of breakwater thing, so not quite accurate)
    
    #rundata.gaugedata.gauges.append([129, 143.324564, 42.293637, 0., 1.e10]) # tokachi ko
    #rundata.gaugedata.gauges.append([111, 144.37100220, 42.97560120, 0., 1.e10]) # Kushiro

    return rundata
    # end of function setrun
    # ----------------------


#-------------------
def setgeo(rundata):
#-------------------
    """
    Set GeoClaw specific runtime parameters.
    For documentation see ....
    """

    try:
        geo_data = rundata.geo_data
    except:
        print("*** Error, this rundata has no geo_data attribute")
        raise AttributeError("Missing geo_data attribute")
       
    # == Physics ==
    geo_data.gravity = 9.81
    geo_data.coordinate_system = 2
    geo_data.earth_radius = 6367.5e3

    # == Forcing Options
    geo_data.coriolis_forcing = False

    # == Algorithm and Initial Conditions ==
    geo_data.sea_level = 0.0
    geo_data.dry_tolerance = 1.e-3
    geo_data.friction_forcing = True
    geo_data.manning_coefficient =.025
    geo_data.friction_depth = 1e6

    # Refinement settings
    refinement_data = rundata.refinement_data
    refinement_data.variable_dt_refinement_ratios = True
    refinement_data.wave_tolerance = 0.005

    # == settopo.data values ==
    topo_data = rundata.topo_data
    # for topography, append lines of the form
    #    [topotype, fname]
    topo_path = os.path.join(dir, 'new_topo.tt3')
    topo_data.topofiles.append([3, topo_path]) 


    # == setdtopo.data values ==
    dtopo_data = rundata.dtopo_data
    # for moving topography, append lines of the form :   (<= 1 allowed for now!)
    #   [topotype, fname]
    dtopo_path = os.path.join(dir, 'curr_dtopo.tt3')
    dtopo_data.dtopofiles.append([3,dtopo_path])
    dtopo_data.dt_max_dtopo = 0.2


    # == setqinit.data values ==
    rundata.qinit_data.qinit_type = 0
    rundata.qinit_data.qinitfiles = []
    # for qinit perturbations, append lines of the form: (<= 1 allowed for now!)
    #   [fname]

    # == fgout grids ==
    # new style as of v5.9.0 (old rundata.fixed_grid_data is deprecated)
    # set rundata.fgout_data.fgout_grids to be a 
    # list of objects of class clawpack.geoclaw.fgout_tools.FGoutGrid:
    #rundata.fgout_data.fgout_grids = []

       ## Fixed grid monitoring ##
    from clawpack.geoclaw import fgmax_tools

    rundata.fgmax_data.num_fgmax_val = 1 # to save only depth (2 saves depth and speed)
    fgmax_grids = rundata.fgmax_data.fgmax_grids  # empty list to start

    # Now append to this list objects of class fgmax_tools.FGmaxGrid
    # specifying any fgmax grids.

    # Points on a uniform 2d grid:
    fg = fgmax_tools.FGmaxGrid()
    fg.fgno = 1
    # fg.point_style = 2
    # fg.dx = 15 / 3600.  # desired resolution of fgmax grid
    # fg.x1 = 142.424067
    # fg.y1 = 42.049926   # lower left corner
    # fg.x2 = 143.074997
    # fg.y2 = 42.218267      # upper right corner
    
    # fgmax grid point_style==4 means grid specified as topo_type==3 file:
    fg.point_style = 4
    fg.xy_fname = os.path.join(dir, 'fgmax_pts_topostyle.data')  # file of 0/1 values in tt3 format
    fg.tstart_max = 5. # after rupture (hopefully)
    fg.tend_max = 2*3600. # same as final time for whole run
    fg.dt_check = 0 # monitor every time step
    fg.min_level_check = 4

    # set fgmax attributes
    fgmax_grids.append(fg)    # written to fgmax_grids.data

    return rundata
    # end of function setgeo
    # ----------------------



if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    from clawpack.geoclaw import kmltools

    rundata = setrun(*sys.argv[1:])
    rundata.write()

    #kmltools.make_input_data_kmls(rundata)
