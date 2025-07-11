"""
Create topo and dtopo files needed for this example:
    etopo10min120W60W60S0S.asc        download from GeoClaw topo repository
    dtopo_usgs100227.tt3              create using Okada model 
Prior to Clawpack 5.2.1, the fault parameters we specified in a .cfg file,
but now they are explicit below.
    
Call functions with makeplots==True to create plots of topo, slip, and dtopo.
"""

from __future__ import absolute_import
from __future__ import print_function
import os

os.environ['CLAW'] = 'Users/anitamiddleton/Documents/python/clawpack'
os.environ['FC'] = 'gfortran'

import clawpack 
import clawpack.clawutil.data

try:
    CLAW = os.environ['CLAW']
except:
    raise Exception("*** Must first set CLAW enviornment variable")

# Scratch directory for storing topo and dtopo files:
#dir = os.path.join(CLAW, 'geoclaw/examples/urakawa1982/scratch')
dir = '/Users/anitamiddleton/Documents/python/urakawa1982/scratch'

def get_topo(makeplots=False):
    """
    Retrieve the topo file from the GeoClaw repository.
    """
    from clawpack.geoclaw import topotools
    topo_fname = os.path.join(dir, 'GEBCOIceTopo.asc')
    topo_fname2 = os.path.join(dir, 'cropped_hokkaido.asc')

    topotools.swapheader(topo_fname, os.path.join(dir, 'new_topo.tt3'))
    topotools.swapheader(topo_fname2, os.path.join(dir, 'cropped_hokkaido.tt3'))
    topo_fname = 'new_topo.tt3'
    topo_path = os.path.join(dir, topo_fname)
    topo = topotools.Topography(topo_path, topo_type=3)

    print("The extent of the data in longitude and latitude: ")
    print(topo.extent)
    print("topo.delta = ",topo.delta)
    print("15 arcseconds is 1/240  degree = %8.6f degree" % (1./240.))

    if makeplots:
        from matplotlib import pyplot as plt
        topo.plot()
        fname = 'topography.png'
        plt.savefig(fname)
        print("Created ",fname)


    
def make_dtopo(makeplots=False):
    """
    Create dtopo data file for deformation of sea floor due to earthquake.
    Uses the Okada model with fault parameters and mesh specified below.
    """
    from clawpack.geoclaw import dtopotools
    import numpy

    dtopo_fname = os.path.join(dir, "curr_dtopo.tt3")

    # Specify subfault parameters 

    # read in fault model and rupture files from the directory
    fault_geometry_file = os.path.join(dir, 'curr_fault_model.csv')
    rupture_file = os.path.join(dir, 'curr_rupt_param.csv')

    fault_mesh = numpy.loadtxt(fault_geometry_file, delimiter=",", skiprows=1) #path, comma separated values, first row is a header
    fault_mesh[:,[2,5,8]] = 1e3*abs(fault_mesh[:,[2,5,8]]) #array slicing accesses depth element, changing it to be positive meters
    rupture_parameters = numpy.loadtxt(rupture_file, delimiter=",", skiprows=1) # skip header

    ### FOR A STATIC, SINGLE TIME RUPTURE ###
    if 1:
        fault0 = dtopotools.Fault() #create object
        fault0.subfaults = [] #initialize empty list
        nsubfaults = fault_mesh.shape[0]

        for j in range(nsubfaults):
            subfault0 = dtopotools.SubFault() #create new object
            node1 = fault_mesh[j,0:3].tolist() #lon,lat,depth of the first node in each triangle
            node2 = fault_mesh[j,3:6].tolist()
            node3 = fault_mesh[j,6:9].tolist()
            node_list = [node1,node2,node3]
            subfault0.slip = rupture_parameters[j,1] #all dip slip
            subfault0.rake = fault_mesh[j,11] # rake is a single value added in csv writing section of fault_disp
            subfault0.set_corners(node_list, projection_zone='10')
            fault0.subfaults.append(subfault0)


        if os.path.exists(dtopo_fname):
            print("*** Not regenerating dtopo file (already exists): %s" \
                        % dtopo_fname)
            print('Created %s, with static rupture of a Mw %.2f event' % \
                  ("urakawa-oki", fault0.Mw()))

        else:
            print("Using Okada model to create dtopo file")
            
            # specify extent of seafloor deformation (?)
            xlower = 140
            xupper = 145
            ylower = 41.5
            yupper = 43

            # dtopo parameters:
            points_per_degree = 60  # 1 minute resolution
            dx = 1./points_per_degree
            mx = int((xupper - xlower)/dx + 1)
            xupper = xlower + (mx-1)*dx
            my = int((yupper - ylower)/dx + 1)
            yupper = ylower + (my-1)*dx

            x = numpy.linspace(xlower,xupper,mx)
            y = numpy.linspace(ylower,yupper,my)

            dtopo = fault0.create_dtopography(x,y,times=[1.], verbose=False)
            dtopo.write(dtopo_fname, dtopo_type=3)
            print('Created %s, with dynamic rupture of a Mw %.2f event' % \
                  ("urakawa-oki", fault0.Mw()))


    if makeplots:
        from matplotlib import pyplot as plt
        if fault0.dtopo is None:
            # read in the pre-existing file:
            print("Reading in dtopo file...")
            dtopo = dtopotools.DTopography()
            dtopo.read(dtopo_fname, dtopo_type=3)
            x = dtopo.x
            y = dtopo.y
        plt.figure(figsize=(12,7))
        ax1 = plt.subplot(121)
        ax2 = plt.subplot(122)
        fault0.plot_subfaults(axes=ax1,slip_color=True)
        ax1.set_xlim(x.min(),x.max())
        ax1.set_ylim(y.min(),y.max())
        dtopo.plot_dZ_colors(1.,axes=ax2)
        fname = os.path.splitext(os.path.split(dtopo_fname)[-1])[0] + '.png'
        plt.savefig(os.path.join(dir,fname))
        print("Created ",fname)


if __name__=='__main__':
    get_topo(False)
    make_dtopo(False)
