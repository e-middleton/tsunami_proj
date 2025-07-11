# Note: In addition to event directories for each earthquake source, there
# is also a directory `make_B0` for each location. This is set up to do a
# short run with no source in order to save values of the topography `B0`
# before co-seismic subsidence at each fgmax point, which is used in 
# post-processing the fgmax results and producing plots and `.nc` files.
# The results are processed by `topo/make_B0.py` and stored in 
# `topo/input_files/LOC_B0.txt` for each fgmax region `LOC`.


from __future__ import absolute_import
from __future__ import print_function
import os
import numpy as np

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

# Scratch directory for storing topo and dtopo files:
dir = os.path.join(CLAW, 'geoclaw/examples/urakawa1982/scratch')

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
    #probdata.add_param('variable_sea_level', params.variable_sea_level)
    #probdata.add_param('topo_missing', params.topo_missing)
    #probdata.add_param('use_wet_mask', params.use_wet_mask)
    #if params.use_wet_mask:
    #    probdata.add_param('t_stays_dry', params.t_stays_dry)
    #    probdata.add_param('fname_wet_mask', 
    #    os.path.abspath(params.fname_wet_mask))

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
    # x values should be integer multipes of 1/9" 
    # y values should be integer multipes of 1/9" 
    # Note: always satisfied if limits are multiples of 0.01 degree

    # Lower and upper edge of computational domain:
    clawdata.lower[0] = 138.0      # west longitude
    clawdata.upper[0] = 148.0      # east longitude

    clawdata.lower[1] = 38         # south latitude
    clawdata.upper[1] = 46.0       # north latitude

    # Number of grid cells: Coarsest grid 2 degrees
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

    clawdata.restart = False  # True to restart from prior results
    clawdata.restart_file = 'fort.chk00096'

    # -------------
    # Output times:
    #--------------

    # Specify at what times the results should be written to fort.q files.
    # Note that the time integration stops after the final output time.
    # The solution at initial time t0 is always written in addition.

    clawdata.output_style = 1

    if clawdata.output_style==1:
        # Output nout frames at equally spaced times up to tfinal:
        clawdata.num_output_times = 10 # every 10 minute for the first 4 hours
        clawdata.tfinal = 1*600.
        clawdata.output_t0 = True  # output at initial (or restart) time?

    elif clawdata.output_style == 2:
        # Specify a list of output times.
        clawdata.output_times = [0., 514.28571429]

    elif clawdata.output_style == 3:
        # Output every iout timesteps with a total of ntot time steps:
        clawdata.output_step_interval = 1
        clawdata.total_steps = 3
        clawdata.output_t0 = True
        

    clawdata.output_format = 'ascii'      # 'ascii' or 'binary' 

    clawdata.output_q_components = 'all'   # need all
    clawdata.output_aux_components = 'none'  # eta=h+B is in q
    clawdata.output_aux_onlyonce = False    # output aux arrays each frame



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
    clawdata.dt_initial = 0.001

    # Max time step to be allowed if variable dt used:
    clawdata.dt_max = 1e+99

    # Desired Courant number if variable dt used, and max to allow without
    # retaking step with a smaller dt:
    clawdata.cfl_desired = 0.5
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

    # negative checkpoint_style means alternate between aaaaa and bbbbb files
    # so that at most 2 checkpoint files exist at any time, useful when
    # doing frequent checkpoints of large problems.

    clawdata.checkpt_style = 0   # for making B0

    if clawdata.checkpt_style == 0:
        # Do not checkpoint at all
        pass

    elif clawdata.checkpt_style == 1:
        # Checkpoint only at tfinal.
        pass

    elif abs(clawdata.checkpt_style) == 2:
        # Specify a list of checkpoint times.  
        clawdata.checkpt_times = 3600.*np.arange(1,16,1)

    elif abs(clawdata.checkpt_style) == 3:
        # Checkpoint every checkpt_interval timesteps (on Level 1)
        # and at the final time.
        clawdata.checkpt_interval = 5


    # ---------------
    # AMR parameters:
    # ---------------
    amrdata = rundata.amrdata

    # max number of refinement levels:
    amrdata.amr_levels_max = 5

    # List of refinement ratios at each level (length at least mxnest-1)
    # (dx = 2*dy at each level)
    amrdata.refinement_ratios_x = [5, 6, 4, 6, 10]
    amrdata.refinement_ratios_y = [5, 6, 4, 6, 10]
    amrdata.refinement_ratios_t = [5, 6, 4, 6, 10]


    # Specify type of each aux variable in amrdata.auxtype.
    # This must be a list of length maux, each element of which is one of:
    #   'center',  'capacity', 'xleft', or 'yleft'  (see documentation).

    amrdata.aux_type = ['center','capacity','yleft']


    # Flag using refinement routine flag2refine rather than richardson error
    amrdata.flag_richardson = False    # use Richardson?
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
    amrdata.verbosity_regrid = 1  

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
    amrdata.tprint = False      # time step reporting each level
    amrdata.uprint = False      # update/upbnd reporting
    
    # More AMR parameters can be set -- see the defaults in pyclaw/data.py

    # ---------------
    # Regions:
    # ---------------
    #rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    rundata.regiondata.regions = []
    # to specify regions of refinement append lines of the form
    #  [minlevel,maxlevel,t1,t2,x1,x2,y1,y2]
    inf = 1e9 
    regions = rundata.regiondata.regions

    x1,x2,y1,y2 = [rundata.clawdata.lower[0], rundata.clawdata.upper[0], 
               rundata.clawdata.lower[1], rundata.clawdata.upper[1]]

    from clawpack.amrclaw.data import FlagRegion
    flagregion = FlagRegion(num_dim=2)  # so far only 2D supported
    flagregion.name = 'Region_domain'
    flagregion.minlevel = 1
    flagregion.maxlevel = 1
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

    if 0:
        regions.append([1, 1, 0., inf, -180,180,-90,90]) # more than domain
        regions.append([3, 3, 0., 3600., 141, 144, 40, 43]) # area of fault slip
        regions.append([1, 4, 0., inf, 138, 146, 41, 43]) # Domain
        regions.append([4, 5, 0., inf, 142.6, 142.85, 41.9, 42.3]) # urakawa gauge location
        regions.append([4, 5, 0., inf, 143, 143.3, 41.9, 42.2]) # erimo port location
        regions.append([4, 5, 0., inf, 141, 142, 42, 43]) # tomakomai location
        regions.append([5, 5, 0., inf, 142.424067, 143.074997, 42.049926, 42.218267]) # fgmax grid 

    #rundata.add_data(data_FlagRegions.FlagRegionData(num_dim=2), 'flagregiondata')

    # ---------------
    # Gauges:
    # ---------------
    # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    rundata.gaugedata.gauges = []
    # # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
    rundata.gaugedata.gauges.append([129, 142.765722, 42.166085, 0., 1.e10]) # urakawa
    rundata.gaugedata.gauges.append([112, 143.135422, 42.010444, 0., 1e10]) # erimo port location
    rundata.gaugedata.gauges.append([113, 141.613420, 42.614828, 0., 1e10]) # tomakomai (outside of breakwater thing, so not quite accurate)
    
    rundata.gaugedata.gtype = 'stationary'
    rundata.gaugedata.min_time_increment = 1. # seconds between gauge output
    rundata.gaugedata.display_format = "f15.7"  # need enough digits for u,v


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
    # topo_path2 = os.path.join(dir, 'test_topo.tt3') # 30 m land topo

    topo_data.topofiles.append([3, topo_path]) 
    # topo_data.topofiles.append([3, topo_path2])
    # for topography, append lines of the form
    #    [topotype, minlevel, maxlevel, t1, t2, fname]
    #topodir = '/Users/rjl/topo/WA/'
   

    # == setdtopo.data values ==
    dtopo_data = rundata.dtopo_data
    # for moving topography, append lines of the form :   (<= 1 allowed for now!)
    #   [topotype, minlevel,maxlevel,fname]
    dtopo_data = rundata.dtopo_data  # empty list
    # for moving topography, append lines of the form :   (<= 1 allowed for now!)
    #   [topotype, fname]
    dtopo_data.dt_max_dtopo = 0.2


    # == setqinit.data values ==
    
    # for now need the new version of QinitData:
    #import data_Qinit  # eventually merge this into geoclaw.data
    #rundata.replace_data('qinit_data', data_Qinit.QinitData())
    
    rundata.qinit_data.qinit_type = 0
    rundata.qinit_data.qinitfiles = []
    # for qinit perturbations, append lines of the form: (<= 1 allowed for now!)
    #   [minlev, maxlev, fname]

        
    # == fgmax.data values ==
    # MODIFIED FORMAT:
    # Now specify a list of objects of class fgmax_tools.FGmaxGrid
    # specifying any fgmax grids.
    from clawpack.geoclaw import fgmax_tools

    fgmax_grids = rundata.fgmax_data.fgmax_grids  # empty list to start

    fg = fgmax_tools.FGmaxGrid()
    fg.fgno = 1
    
    # fgmax grid point_style==4 means grid specified as topo_type==3 file:
    fg.point_style = 4
    fg.xy_fname = os.path.join(dir, 'fgmax_pts_topostyle.data')  # file of 0/1 values in tt3 format
    fg.tstart_max = 5. # after rupture (hopefully)
    fg.tend_max = 600. # same as final time for whole run
    fg.dt_check = 0 # monitor every time step
    fg.min_level_check = 4


    # set fgmax attributes
    fgmax_grids.append(fg)    # written to fgmax_grids.data
    return rundata
    # end of function setgeo
    # ----------------------:



if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys
    from clawpack.geoclaw import kmltools
    rundata = setrun(*sys.argv[1:])
    rundata.write()
    

