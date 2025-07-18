import os 
import numpy as np


scratch_dir = '/Users/anitamiddleton/Documents/python/tsunami_proj/scratch'

which_test = input("Which test in the scratch directory from this project would you like to run? ")
test_dir = os.path.join(scratch_dir, 'tokachi2003', which_test)

def make_topo():
    topo_fname = os.path.join(scratch_dir, 'curr_topo.tt3')
    if os.path.exists(topo_fname):
        print("Topography file already exists, not regenerating.")
    else:
        from clawpack.geoclaw import topotools
        print("Making topography file...")

        topo_path = os.path.join(scratch_dir, 'GEBCOIceTopo.asc')
        topotools.swapheader(topo_path, os.path.join(scratch_dir, 'curr_topo.tt3')) 

        # output extent
        new_topo_path = os.path.join(scratch_dir, "curr_topo.tt3")
        topo = topotools.Topography(new_topo_path, topo_type=3)
        print("The extent of the data in longitude and latitude: ")
        print(topo.extent)


# checks for dtopo, if it does not exist, writes dtopo
def make_dtopo():
    from clawpack.geoclaw import dtopotools

    dtopo_fname = os.path.join(test_dir, "dtopo.tt3")

    if os.path.exists(dtopo_fname):
            print("*** Not regenerating dtopo file (already exists): %s" \
                        % dtopo_fname)
    else: 
        fault_geometry_file = os.path.join(test_dir, 'fault_model.csv')
        rupture_file = os.path.join(test_dir, 'rupt_param.csv')

        fault_mesh = np.loadtxt(fault_geometry_file, delimiter=",", skiprows=1) #path, comma separated values, first row is a header
        fault_mesh[:,[2,5,8]] = 1e3*abs(fault_mesh[:,[2,5,8]]) #array slicing accesses depth element, changing it to be positive meters
        rupture_parameters = np.loadtxt(rupture_file, delimiter=",", skiprows=1) # skip header

        ### FOR A MULTI-TIME RUPTURE ###
        # create fault object
        fault0 = dtopotools.Fault()
        fault0.subfaults = []
        fault0.rupture_type = 'kinematic'

        J = int(np.floor(fault_mesh.shape[0]))

        # read in sub fault and rupture information
        for j in range(J):
            subfault0 = dtopotools.SubFault()
            node1 = fault_mesh[j,0:3].tolist()
            node2 = fault_mesh[j,3:6].tolist()
            node3 = fault_mesh[j,6:9].tolist()
            node_list = [node1,node2,node3]

            subfault0.set_corners(node_list, projection_zone='10')
            subfault0.rupture_time = rupture_parameters[j,2]
            subfault0.rise_time = rupture_parameters[j,1]
            subfault0.rake = fault_mesh[j,9]

            subfault0.slip = rupture_parameters[j,0]
            fault0.subfaults.append(subfault0)

            print("Using Okada model to create dtopo file")
            
            x,y = fault0.create_dtopo_xy(dx = 4/60.) #what is dx?
            print('Will create dtopo on arrays of shape %i by %i' % (len(x),len(y)))
            tfinal = max([subfault1.rupture_time + subfault1.rise_time for subfault1 in fault0.subfaults])
            times0 = np.linspace(0.,tfinal,100)
            dtopo0 = fault0.create_dtopography(x,y,times=times0,verbose=True);
            dtopo0.write(dtopo_fname, dtopo_type=3)

            print('Created %s, with dynamic rupture of a Mw %.2f event' % (dtopo_fname, fault0.Mw()))



# checks for fgmax grid points / RuledRectangle / fgmaxB0
def make_fgmax():
    from clawpack.amrclaw import region_tools
    from clawpack.geoclaw import topotools, marching_front, fgmax_tools

    fgmax_pts_fname = scratch_dir + '/tokachi2003/fgmax_pts_topostyle.txt'
    ruledRectangle_fname = scratch_dir + '/tokachi2003/RuledRectangle_fgmax.txt'

    if os.path.exists(fgmax_pts_fname):
        if os.path.exists(ruledRectangle_fname):
            print("*** Not regenerating fgmax or RuledRectangle file (already exists)")
        else:
             print("fgmax file exists, but Ruled Rectangle does not, please delete fgmax file and rerun make_inputs.py")

    # creates fgmax files needed 
    # currently, uses a topo file, and there is the option to 
    # separate out coastline points, but the entire topo file is used here as a plain rectangle
    else:
        topo_path = os.path.join(scratch_dir, 'curr_topo.tt3')
        topo = topotools.Topography(topo_path, topo_type=3)
        topo = topo.crop(filter_region=[143, 146, 41.75, 43.25])

        pts_chosen = marching_front.select_by_flooding(topo.Z, Z1=0, Z2=1e10, max_iters=None)

        # add on points that are between 0 and 15 meters elevation along the coastline to the original set
        pts_chosen = marching_front.select_by_flooding(topo.Z, Z1=0, Z2=15.,
                                                    prev_pts_chosen=pts_chosen,
                                                    max_iters=None)

        pts_chosen_shallow = marching_front.select_by_flooding(topo.Z, Z1=0, Z2=-1.e10, max_iters=None)

        # find the intersection of the onshore coastal points from the previous code cell
        # with the shallow bathymetry points found above 
        # for a complete set of fgmax points along the coast and in the shallow waters around them
        pts_chosen_nearshore = np.logical_and(pts_chosen, pts_chosen_shallow)

        fname_fgmax_mask = os.path.join(scratch_dir, 'tokachi2003/fgmax_pts_topostyle.txt')
        topo_fgmax_mask = topotools.Topography()
        topo_fgmax_mask._x = topo.x
        topo_fgmax_mask._y = topo.y
        topo_fgmax_mask._Z = np.where(pts_chosen_nearshore, 1, 0)  # change boolean to 1/0
        topo_fgmax_mask.generate_2d_coordinates()

        topo_fgmax_mask.write(fname_fgmax_mask, topo_type=3, Z_format='%1i')
        print('Created %s' % fname_fgmax_mask)

        rr = region_tools.ruledrectangle_covering_selected_points(topo.X, topo.Y, pts_chosen,
                                                          ixy='y', method=0,
                                                          padding=0, verbose=True)
        rr.write(os.path.join(scratch_dir, 'tokachi2003/RuledRectangle_fgmax.txt'))

def check_B0():
    fgmax_ptsB0_fname = scratch_dir + '/tokachi2003/tokachi2003_B0.txt' # or other name of the fgmax grid's B0 file
    if os.path.exists(fgmax_ptsB0_fname):
        print("B0 file for fgmax points exists, no further steps needed.")
        print()
    else:
        print()
        print("The B0 file for the fgmax grid does not exist.")
        print("Please open params.py in the project directory, and set makeB0 to True")
        print("Then, do a geoclaw run as normal.")
        print("Once the geoclaw run has finished, run")
        print("python writeB0.py")
        print("This will create the appropriate file for using to parse the fgmax grid outputs later.")
        print("Do not forget to set makeB0 to False after this has been completed.")
        print("Failure to set it to false will mean that no rupture information is included in the geoclaw run.")
        print()

# creates fgmax grid and RuledRectangle

if __name__=='__main__':
    print()
    make_topo()
    make_dtopo()
    make_fgmax()
    check_B0()