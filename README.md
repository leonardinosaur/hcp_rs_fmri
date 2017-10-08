## hcp_rs_fmri
Generating connectivity matrix from resting-state fMRI data from the Human Connectome Project. 
  
To process a single time-series, use hcpExtractNetwork. This script performs basic checks to make  
sure arguments are called properly and input files exist, and then calls on the functions  
in rs_tools.py to do the heavy-lifting/number crunching. A typical use case would look like:
  
~~~
$ python hcpExtractNetowrk.py -i PATH_TO_4D_VOLUME.nii.gz -o PATH_TO_CONNECTIVITY MATRIX.npy -a aparc+aseg.nii.gz
~~~
  
For more information on usage, please run:  
  
~~~~
$ python hcpExtractNetwork.py --help
~~~~
  
# Batch processing

To process multiple datasets, use hcpExtractNetworks. This script sets-up
$HOME/extractjobs/ and a .sh script that can be submitted to the grid engine
for parallel processing. An example usage:
  
~~~
$ python hcpExtractNetworks.py -i INPUTLIST -a aparc+aseg.nii.gz -d OUTPUTDIR
~~~
  
Where INPUTLIST is a text file that lists (one per line) full paths to 4D volumes
and OUTPUTDIR is the directory where the matrices will be saved. After this hcpExtractNetworks
finishes running, it will print out a command that you can run from $HOME/extractjobs to
submit your job for processing. Output and error text files will be saved to
$HOME/extractjobs/sgeout/

# Requirements
Pandas, NumPy, NiBabel

