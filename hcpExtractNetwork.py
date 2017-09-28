"""

hcpExtractNetwork

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

Not yet implemented.

A 3D Nifti volume with voxel labels, each unique label denoting
a unique ROI. If this option is used, the average time series from
each unique ROI will be calculated. In the resulting connectivity matrix,
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
extension, it will be added.


--force

Not yet implemented.

Overwrite existing connectivity matrix with same path as OUTPUT

--uptri

Not yet implemented.

Only save upper right triangle of connectivity matrix. Set the
lower left triangle to zero. 

--mni

Not yet implemented

Check if input volumes are in MNI152 2mm space before attempting
to extract network.


Notes/To-do's:
==============
-Write some tests
-Currently only supports nifti volumes; should probably add
	ability to handle .mgz
-Add file exists check to matrix saving
-Make sure to only get fmri data from voxels in MNI brain
-Should probably change sys.exits to 'raise *Error' instead
-To think about it, this code can also be used for PET, instead
of doing correlations across time, PET volumes can be concatenated
into a 4D file and then you can do a correlation across subjects

Bug Submits
============
Please report bugs to leonardinodigma@gmail.com


Written on 28 Sept 2017 by Dino
Last Updated on 28 Sept 2017 by Dino
	
	-Skeleton and pseudo code for network extract scripts
	-Don't use yet

"""
import os
import sys

import argparse
from rs_extract_networks import *

parser = argparse.ArgumentParser(usage=__doc__)


parser.add_argument('-i', '--input', help = 'Input 4D time-series volume')
parser.add_argument('-o', '--output', help = 'Output')
parser.add_argument('-a', '--aseg', help = 'Input segmentation/parcellation file')
parser.add_argument('-b', '--bmasks', help = 'Input text file with paths to binary ROI masks')
parser.add_argument('-m', '--mni', help = 'Add checks to assume MNI152 2mm space')
parser.add_argument('-ut', '--uptri', help = 'Only save the upper right triangle of the matrix and set \n \
												the lower left to zeroes')


args = parser.parse_args()

if not args.input:
	sys.exit('Error: need 4D time-series volume input')

if not os.path.exists(args.input):
	sys.exit('Error: 4D time-series volume does not exist')


if args.bmasks:
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

	err_code = extract_network_bmasks(args.input, rm_paths, args.output)
	
	if err_code:
		sys.exit('Error: failed generating network')
	else:
		print 'Successfully extracted network and connectivity matrix'




if args.aseg:
	print "Hello world!"












