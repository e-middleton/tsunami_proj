# plot combined gauge results from all gauges and their observations to compare
import matplotlib.pyplot as plt

from setplot import setplot
plotdata = setplot()

# Process observation data
import os 
import numpy as np

# Read in observations for Urakawa
scratch_dir = '/Users/anitamiddleton/Documents/python/tsunami_proj/scratch/tokachi2003'
gauge_path = os.path.join(scratch_dir, 'tide_gauge_observations/urakawa.csv') # observed tide gauge data

observed_urakawa = np.loadtxt(gauge_path, delimiter=',', skiprows=1) # x,y time,height
observed_urakawa[:,0] = observed_urakawa[:,0]*60

# observations for Kushiro

gauge_path = os.path.join(scratch_dir, 'tide_gauge_observations/kushiro.csv') # observed tide gauge data
observed_kushiro = np.loadtxt(gauge_path, delimiter=',', skiprows=1) # x,y time,height


# observations for Tokachikou

gauge_path = os.path.join(scratch_dir, 'tide_gauge_observations/tokachi.csv') # observed tide gauge data
observed_tokachi = np.loadtxt(gauge_path, delimiter=',', skiprows=1) # x,y time,height

outdir = '/Users/anitamiddleton/Documents/python/tsunami_proj/outputs/tokachi2003/_output'
time_shift = 10 # 10 minutes
plotdata.outdir = outdir 
g129 = plotdata.getgauge(129)
t = (g129.t / 60.) + time_shift # convert to minutes 
eta = g129.q[3,:]   # eta = h + B (depth plus bathymetry)

g111 = plotdata.getgauge(111)
t2 = (g111.t / 60.) # convert to minutes 
eta2 = g111.q[3,:]   # eta = h + B (depth plus bathymetry)

g112 = plotdata.getgauge(112)
t3 = (g112.t / 60.) + time_shift # convert to minutes and shift
eta3 = g112.q[3,:]   # eta = h + B (depth plus bathymetry)

# plot the comparison

fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
fig.suptitle('Sea Surface Elevation at Tide Gauges')
ax1.set_title("Urakawa (+timeshift)")
ax1.plot(t,eta, 'r.-', markersize=1, label='GeoClaw')
ax1.plot(observed_urakawa[:,0], observed_urakawa[:,1], 'k.-', markersize=5, label='Observation') 
ax1.plot(t,0*t, 'k-', label='Sea level', linewidth=0.5)
ax1.grid(True)
#ax1.set_ylabel("meters")

ax2.set_title("Kushiro")
ax2.plot(t2,eta2, 'r.-', markersize=1, label='GeoClaw')
ax2.plot(observed_kushiro[:,0]*60, observed_kushiro[:,1], 'k.-', markersize=5, label='Observation') # cm to m in erimo observations
ax2.plot(t2,0*t2, 'k-', label='Sea level', linewidth=0.5)
ax2.grid(True)
ax2.set_ylabel("meters")

ax3.set_title("Tokachikou (+timeshift)")
ax3.plot(t3,eta3, 'r.-', markersize=1, label='GeoClaw')
ax3.plot(t3,0*t3, 'k-', label='Sea level', linewidth=0.5)
ax3.plot(observed_tokachi[:,0]*60, observed_tokachi[:,1]*100, 'k.-', markersize=5, label='Observation') 
ax3.grid(True)
ax3.set_ylim(-0.3, 0.3)
plt.xlim(0,240)
plt.xlabel('minutes since earthquake')
#plt.ylabel('meters')
plt.legend(bbox_to_anchor=(-0.05, 3.905), loc='upper left', borderaxespad=0.)

plt.show()