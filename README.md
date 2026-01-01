# Project for tsunami simulation using modeled earthquakes around Hokkaido, Japan.

## Installations
This project requires the software package clawpack from 
https://www.clawpack.org/developers.html#installation-instructions-for-developers 
This was created using the most recent version as of June 2025
follow the download instructions in the link and use the virtual environment created to run the projects in this repo.

There are three separate projects

## Projects

urakawa1982

ishikari

tokachi

They all have identical setrun.py files, and any changes for clawpack or output formatting (e.g., tide gauge locations or resolution levels) are controlled by the params.py file in each project directory.

The project directories in the scratch folder contain the tests run for each project, 
take care with file names, because all of the tests have identically named fault_model.csv, rupt_param.csv, and dtopo.tt3 files.
They are kept separate in their test folders, and if removed, can easily become mixed up.

## Input files

B0.txt - The original, undeformed topography file within the fgmax monitoring perimeter <br>
RuledRectangle_fgmax.txt - a rectangular region for grid monitoring of sea level height <br>
fault_model.csv - the mesh model of the fault where an earthquake is being simulated <br>
rupt_param.csv - the simulated rupture along the fault elements <br>
dtopo.tt3 - the deformed topography file created from the simulated rupture, fault mesh, and original topography files

## Running tests
In order to run a test, first set the environment variables for: <br>

export PROJ = /directory/of/this/github/repo <br>
export OUTPUT = /project/directory/within/outputs/folder <br>
export CLAW = /clawpack/installation/location <br>
export FC = gfortran <br>

Example test run: 
Activate the virtual environment where clawpack has been installed, e.g.

*conda activate clawpack*

Then move into the project directory that corresponds to the test you want to run,  

*cd tokachi*

Make sure all inputs are present before running

*python make_inputs.py*

Which should then output 

*Which test in the scratch directory from this project would you like to run?* test1_TWC

Follow any directions the output gives, if no instructions are given, run

*make .output* or *make .plots*

It will then confirm,

*Which test in the scratch directory from this project would you like to run?* test1_TWC

Then it should run the geoclaw simulation, and outputs can be saved to the images folder of outputs, and 
sorted through using the view_results.ipynb for that particular project.

