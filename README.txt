
This project requires the software package clawpack from 
https://www.clawpack.org/developers.html#installation-instructions-for-developers 
follow the download instructions in the link and use the virtual environment created to run the projects in this repo.

There are three separate projects

urakawa1982
ishikari
tokachi

They all have identical setrun.py files, and the changes are controlled by the params.py file in each project directory.
The project directories in the scratch folder contain the tests run for each project, 
take care with file names, because all of the tests have identically named fault_model.csv, rupt_param.csv, and dtopo.tt3 files.
They are kept separate in their test folders, and if removed, can easily become mixed up.

# In order to run a test, first set the environment variables for 

export PROJ = points to the directory where this repo is
export OUTPUT = points to the project directory in the outputs folder
export CLAW = points to the directory where clawpack was installed/cloned
export = FC - gfortran

# then activate the virtual environment where clawpack has been installed, e.g.

conda activate clawpack

# Then change into the project directory that corresponds to the test you want to run,  

cd tokachi

# then make sure all inputs are present

python make_inputs.py
Which test in the scratch directory from this project would you like to run? test1_TWC

# follow any directions it gives, if no instructions are given, run

make .output or make .plots

# It will then ask again,

Which test in the scratch directory from this project would you like to run? test1_TWC

# then it should run the geoclaw simulation, and outputs can be saved to the images folder of outputs, and 
# sorted through using the view_results.ipynb for the project.

