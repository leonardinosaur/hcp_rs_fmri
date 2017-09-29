# hcp_rs_fmri
Processing and analysis of resting-state fMRI data from the Human Connectome Project  
  
The primary point of entry is hcpExtractNetwork. This script performs basic checks to make  
sure arguments are called properly and input files exist, and then calls on the functions  
in rs_extract_networks.py and rs_tools.py to do the heavy-lifting/number crunching. For more  
information on usage, please run:  

~~~~
$ python hcpExtractNetwork --help
~~~~
  

