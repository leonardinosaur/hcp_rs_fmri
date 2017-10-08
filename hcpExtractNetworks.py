"""

hcpExtractNetworks.py


A script to set-up a *.sh job that can be submitted to
	SGE to run hcpExtractNetwork.py on multiple datasets
	in parallel. After running, this script will print out
	the command that you can run from $HOME/extractjobs/
	to submit the *.sh job for processing.

Numpy arrays will be saved with randomly generated filenames (e.g. 
	tmp_aSdf42.npy). This was implemented since many input files will likely
	have identical file names and to take burden off user from having to specify
	output file names. After the numpy array is generated, an accompanying textfile (e.g.
	tmp_aSdf42.txt) will be saved along with the array. This text files
	lists which inputs were used to generate the numpy array. This text file
	can be easily parsed to rename output .npy files.
  
For further information, please see hcpExtractNetwork.py


--input

A text file that lists full paths (one per line) to input 4D volumes

--outdir

Directory where connectivity matrices will be saved

--aseg

A path to a 3D segmentation volume. This segmentation will be applied to
	all of the 4D volumes specified in INPUT

--bmasks

Not yet implemented for batch processing.
This option has been implemented for single case processing so
	please refer to hcpExtractNetwork


Written on 27 Sept 2017 by Dino
Last updated on 7 Oct 2017 by Dino
	-Set-up SGE stuff

To-do:
-Remove unused imports

"""
import argparse
import shutil
import os
from glob import glob
import pandas as pd
import os
import random

parser = argparse.ArgumentParser(usage=__doc__)


parser.add_argument('-i', '--input', help = 'Text file that lists full paths (one per line) to input 4D time-series volumes')
parser.add_argument('-d', '--outdir', help = 'Output directory where matrices will be saved')
parser.add_argument('-a', '--aseg', help = 'Input segmentation/parcellation file')
parser.add_argument('-b', '--bmasks', help = 'Input text file with paths to binary ROI masks')



args = parser.parse_args()

# Make an output directory in home
sge_dir =  os.path.expanduser('~')+ '/extractjobs/'
sge_out_dir = sge_dir + 'sgeout'

if not os.path.exists(sge_dir):
	os.system('mkdir %s' % sge_dir)
	os.system('mkdir %s' % sge_out_dir) 

if not os.path.exists(sge_dir + 'output.options'):
	with open(sge_dir + 'output.options', 'w') as o:
		o.write('-o %s\n' % sge_out_dir)
		o.write('-e %s' % sge_out_dir)
		

# Generate .sh file name
prev_jobs = glob(sge_dir + 'job_extract_network*.sh')
job_name = 'job_extract_network_%s.sh' % (str(len(prev_jobs)))
job_inps = 'job_extract_network_%s.inputs' % (str(len(prev_jobs)))

# Create text file for list of subjects
shutil.copy(args.input, sge_dir + '/' + job_inps) 

# Write the script to submit
with open(sge_dir + job_name, 'w') as w:
	w.write('#!/bin/sh\n')
	w.write('DATASET="${SGE_TASK}"\n')
	if args.aseg:
		cmd = 'python /home/jagust/dino/scripts/hcp/hcpExtractNetwork.py -i $DATASET -a %s -d %s \n' % (args.aseg, args.outdir) 
		w.write(cmd)
	elif args.bmasks:
		sys.exit('Not yet implemented')
	else:
		sys.exit('Error: need to specify segmentation(s) with -a or -b')


print 'Navitgate to %s and type this command: \n\t submit -s %s -f %s -o output.options' % (sge_dir, job_name, job_inps)
