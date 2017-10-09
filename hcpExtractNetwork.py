"""

hcpExtractNetwork.py

Extracts network from preprocessed HCP rs-fMRI volume and saves
	the connectivity matrix in a NumPy array. The functional network
	atlas can be specified in two ways different ways:

	(1) A single 3D segmentation/parcellation volume with
			labels to denote ROIs
	(2) A text file that lists (one per line) paths to
			binary ROI masks (see below for further details)



--input

A 4D Nifti volume with preprocessed fMRI data

--aseg

A 3D Nifti volume with voxel labels, each unique label denoting
a unique ROI. In the resulting connectivity matrix,
indices will be ordered by increasing label value. For example, if
42 is the label in ASEG with the lowest value (other than 0 of course),
then values in row 0 and values in column 0 in the output matrix will
represent the edge weights of the ROI that is denoted by 42.

--bmasks

A text file with a list of paths (one per row) to binary ROI masks.
Will assume that any non-zero voxel in the volume is part of the ROI.
Each ROI will be treated as a seperate node in the the resulting functional
network. If this option is used, the indices in the output matrix will be
ordered by the order in the list of paths. For example, if 'Precuneus.nii.gz'
is the first path in BMASKS and it represents the precuneus
ROI, then values in row 0 and values in column 0 in the output matrix will
represent the edge weights of the precuneus node.

--output

Output file name for connectivity matrix. If the name doesnt have a .npy
extension, it will be added. If this option is left blank, a random
file name will be generated.

--outdir

Output directory; only used if -o/--output is not specified; Matrices
will be saved into this directory with a random file name. An accompanying
text file will be saved along with the matrix to help identify the output.

--fsflag

Only extract connectivity matrix for grey matter ROIs from the Desikan-Killiany
atlas. Identifies these grey matter ROIs using default FreeSurfer LUT. Assumes
that -a/--aseg option is being used and a FreeSurfer generated aparc+aseg.nii.gz
file is supplied.

--uptri

Not yet implemented.

Only save upper right triangle of connectivity matrix. Set the
lower left triangle to zero. 


--force

Not yet implemented.

Overwrite existing connectivity matrix with same path as OUTPUT


Notes/To-do's:
==============
-Write some tests
-Currently only supports nifti volumes; should probably add
	ability to handle .mgz
-Should probably change sys.exits to 'raise *Error' instead
-To think about it, this code can also be used for PET, instead
of doing correlations across time, PET volumes can be concatenated
into a 4D file and then you can do a correlation across subjects

Bug Submits
============
Please report bugs to leonardinodigma@gmail.com


Written on 28 Sept 2017 by Dino
Last Updated on 7 Oct 2017 by Dino
	-Added fs_flag to include only Desikan gray matter ROIs
	in connectivity matrix

"""
import os
import sys

import argparse
from rs_tools import *
from datetime import datetime

print str(datetime.now())
start = str(datetime.now())
parser = argparse.ArgumentParser(usage=__doc__)


parser.add_argument('-i', '--input', help = 'Input 4D time-series volume')
parser.add_argument('-o', '--output', help = 'Output matrix file name')
parser.add_argument('-d', '--outdir', help = 'Output directory; only used if -o/--output is not specified')
parser.add_argument('-a', '--aseg', help = 'Input segmentation/parcellation file')
parser.add_argument('-b', '--bmasks', help = 'Input text file with paths to binary ROI masks')
parser.add_argument('-fs','--fsflag', default = False, action = 'store_true', help = 'Only include labels for Desikan grey matter ROIs')
parser.add_argument('-ut', '--uptri', default = False, action = 'store_true', help = 'Only save the upper right triangle of the matrix and set \n \
												the lower left to zeroes')


args = parser.parse_args()

# Check if inputs exist
if not args.input:
	sys.exit('Error: need 4D time-series volume input')

if not os.path.exists(args.input):
	sys.exit('Error: 4D time-series volume does not exist')



err_code = 0

# First option - passing in a direct path to an aseg volume
if args.aseg:
    if not os.path.exists(args.aseg):
	sys.exit('Error: input text file %s does not exist' % args.aseg)
    
    if args.output:
            err_code = extract_network_aseg(args.input, args.aseg, args.output)
    else:
    	# Output not specified so random one will be generated
        out_path = 'tmp_' + generate_random_key() + '.npy'
        if args.outdir and len(args.outdir) > 2:
			if not os.path.exists(args.outdir):
				os.system('mkdir %s' % args.outdir)
			out_path = args.outdir + '/' + out_path
    	with open(out_path.replace('.npy', '.txt'), 'w') as w:
            w.write(args.input + '\n')
	    w.write(args.aseg + '\n')
	    w.write(out_path)

	    # Extract connectivity matrix
	    err_code = extract_network_aseg(args.input, args.aseg, out_path, fs_flag = args.fsflag)



# Second option - inputting list of paths to binary ROI masks
elif args.bmasks:
	if not os.path.exists(args.bmasks):
		sys.exit('Error: input text file %s does not exist' % args.bmasks)

	rm_paths = []
	with open(args.bmasks, 'r') as r:
		rmasks = r.readlines()
		for rmask in rmasks:
			if not os.path.exists(rmask.replace('\n', '')):
				# Maybe at some point, this should be a warning
				sys.exit('Error: binary ROI mask %s does not exist' % rmask)
			else:
				rm_paths.append(rmask.replace('\n', ''))

	if args.output:
		err_code = extract_network_bmasks(args.input, rm_paths, args.output)
	else:
		out_path = 'tmp_' + generate_random_key() + '.npy'
		if args.outdir:
			if not os.path.exists(args.outdir):
				os.system('mkdir %s' % args.outdir)
                	out_path = args.outdir + '/' + out_path
		with open(out_path.replace('.npy', '.txt'), 'w') as w:
			w.write(args.input + '\n')
		 	for rp in rm_paths:
				w.write(rp + '\n')
			w.write(out_path)

		# Extract connectivity matrix
		err_code = extract_network_bmasks(args.input, rm_paths, out_path)

else:
	print 'Segmentation file(s) required to generate matrix...'
	err_code = 1


# Exit script
if err_code:
	print 'Error: failed generating network'
        print 'Started at: ', start
        print 'Exited at: ', str(datetime.now())

else:
	print 'Successfully extracted network and connectivity matrix!'
	print 'Started at: ', start
	print 'Ended at: ', str(datetime.now())











