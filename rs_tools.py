'''
rs_tools

Functions for working with preprocessed HCP rs-FMRI data



Written on 28 Sept 2017 by Dino
Last Updated on 3 Oct 2017 by Dino
	-Implemented extract_network_aseg


'''

import nibabel as ni
import numpy as np
import os
import random
import pandas as pd
from datetime import datetime

fsl_dir = os.environ['FSL_DIR']
MNI_MASK_PATH = fsl_dir + '/data/standard/MNI152_T1_2mm_brain_mask.nii.gz'

fs_gm_df = pd.read_csv('/home/jagust/graph/scripts/fs_gm.csv', header=None)
fs_gm_df.columns = ['ROI', 'Label']
fs_rois = fs_gm_df['Label'].values

def extract_network_aseg(infname, aseg_path, outfname, \
	fs_flag=False, force_flag=False, uptri_flag=False):
	"""Extracts and saves connectivity matrix using 4D time-series volume and
		3D segmentation volume

		Args:
			infname: path to inpute 4D time series volumes
			aseg_path: path to segmentation/parcellation volume
			outfname: output file name for connectivity matrix

		Returns:
			int: Error code

	"""

        print 'Reading timeseries data...'
        ts_data, err_code = read_ts_data(infname)
        if err_code:
                print 'Problem reading time-series volumes...'
                return 1
        
        print 'Timeseries data loaded'
        ts_df = pd.DataFrame()
        aseg_data, err_code = read_aseg_data(aseg_path)
        ts_df = calc_rois_ts(ts_data, aseg_data, fs_flag)

        corr_df = ts_df.corr()
        corr_mat = corr_df.values

        print 'Saving connectivity matrix'
        write_array(corr_mat, outfname)

        return 0

def extract_network_bmasks(infname, aseg_paths, outfname, \
		force_flag=False, uptri_flag=False):
	"""Extracts and saves connectivity matrix using 4D time-series volume and
		3D segmentation volume

		Args:
			infname: path to inpute 4D time series volumes
			aseg_paths: list of paths to binary ROI mask volumes
			outfname: output file name for connectivity matrix

		Returns:
			int: Error code

	"""

	print 'Reading timeseries data...'
	ts_data, err_code = read_ts_data(infname)
        if err_code:
                print 'Problem reading time-series volumes...'
                return 1
        print 'Timeseries data loaded'
        ts_df = pd.DataFrame()
	print 'Calculating mean values for each ROI at each timepoint'
	aseg_vol, err_code = clobber_bmasks(aseg_paths)
	ts_df  = calc_rois_ts(ts_data, aseg_vol)

        corr_df = ts_df.corr()
        corr_mat = corr_df.values

        print 'Saving connectivity matrix'
        write_array(corr_mat, outfname)

	return 0


def clobber_bmasks(aseg_paths):
	"""Clobbers binary ROI masks into single segmentation volume
		
		Args:
			aseg_paths: List of paths to binary ROI mask volumes

		Returns:
			numpy array: Segmentation volume where voxels have labels
				denoting ROI
			int: error code

	"""

	# Load first aseg
	aseg_data, err_code = read_aseg_data(aseg_paths[0])
	if err_code:
		print 'Error: error reading first binary ROI mask; \
			cannot make a clobbered aseg volume'
		return np.array([]), 1

	aseg_vol = np.zeros(aseg_data.shape)	


	curr_label = 1
	aseg_vol[np.where(aseg_data != 0)] = curr_label
	curr_label += 1
	
	for apath in aseg_paths[1:]:
		aseg_data, err_code = read_aseg_data(apath)
		if aseg_data.shape == aseg_vol.shape:
			aseg_vol[np.where(aseg_data != 0)] = curr_label
			curr_label += 1 
		else:
			err_code = 1
			return np.array([]), err_code
	return aseg_vol, 0


def read_ts_data(img_path):
	"""Read 4D time-series volume
	
		Args:
			img_path: Path to 4D volume

		Returns:
			numpy array: 4D volume data; empty if reading
			int: error code

	"""
	err_code = 0

	# Should probably change this to accept .mgz files too
	if (not img_path.endswith('.nii.gz')) and (not img_path.endswith('.nii')):
		err = 'Error: time-series volume must be .nii/.nii.gz format'
		print err
		err_code = 1
		return np.array([]), err_code

	# Load image
	img = ni.load(img_path)
	img_data = img.get_data()
	img_shape = img_data.shape

	if len(img_shape) != 4:
		err='Error: time-series volume must be 4D; input volume has %s dimension(s)' % (str(len(img_shape)))
		print err
		err_code = 1

	return img_data, err_code

def read_aseg_data(img_path):
	"""Read segmentation volume
	
		Args:
			img_path: Path to 3D volume

		Returns:
			numpy array: 4D volume data; empty if reading
			int: error code


	"""

	err_code = 0
	
	# Should probably change this to accept .mgz files too
	if (not img_path.endswith('.nii.gz')) and (not img_path.endswith('.nii')):
		err = 'Error: aseg  volume must be .nii/.nii.gz format'
		print err
		err_code = 1
		return np.array([]), err_code

	# Load image
	img = ni.load(img_path)
	img_data = img.get_data().squeeze()
	img_shape = img_data.shape

	if len(img_shape) != 3:
		err='Error: aseg volume must be 3D; input has %s dimensions' % (str(len(img_shape)))
		print err
		err_code = 1

	return img_data, err_code



def write_array(mat, outfname, force_flag = False):
	"""Write numpy array to file
		Args:
			mat: Numpy array to write
			outfname: output filename

	"""
	if os.path.exists(outfname) or os.path.exists(outfname + '.npy'):
		randid = generate_random_key()
		rand_outfname = 'tmp_' + randid + '.npy'
		wrn = 'Warning: file %s already exists. Writing results to %s ' % (outfname, rand_outfname)
		np.save(rand_outfname, mat)
	else:
		np.save(outfname, mat)

def calc_rois_ts(img_data, aseg_data, fs_flag=True):
	"""Calculate average time-series from each ROI
		Args:
			img_data: 4D Time series volume data
			aseg_data: Segmentation volume data

		Returns:
			pandas DataFrame: With dimensions # ROIs x # of timepoints in IMG_DATA

	"""

	labels = get_aseg_labels(aseg_data)
	if fs_flag:
		labels = [l for l in labels if l in fs_rois]
	out_df = pd.DataFrame(columns = labels)
	print 'Input time series data has %s timepoints' % img_data.shape[3]
	for i in range(img_data.shape[3]):
		tp_data = img_data[:, :, :, i]
		roi_means = []
		for label in labels:
			roi_means.append(calc_roi_mean(tp_data, aseg_data, label))
		out_df.loc[len(out_df)] = roi_means
	print 'Calculated ROI mean data for %s timepoints' % str(len(out_df))
	return out_df

def calc_roi_mean(img_data, aseg_data, label):
	"""Calculate mean value in an ROI
		Args:
			img_data: 3D volume with functional values
			aseg_data: 3D segmentation volume
			label: Label of ROI in ASEG_DATA

		Returns:
			float: Mean value in IMG_DATA of the ROI denoted by LABEL

	"""
	if len(img_data.shape) != 3 or len(aseg_data.shape) != 3:
		print 'Error: time point data or aseg data is not 3D'
		return -4
	else:
		return np.mean(img_data[np.where(aseg_data == label)])

def get_aseg_labels(aseg_data):
	"""Extract labels from segmentation volume
		Args:
			aseg_data: 3D segmentation volume data
		
		Returns:
			list: List of unique values in aseg_data (labels) excluding 0

	"""
	labels = sorted(list(set(aseg_data.flatten())))
	return [l for l in labels if l != 0]

def generate_random_key():
	"""Generate random alphanumeric string of length 16

		Returns:
			str: Alphanumeric string

	"""
	alpha_num = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(alpha_num) for i in range(16))







### EVERYTHING BELOW IS NOT DONE ####
def write_nifti_volume(img_data, img_affine, outfname, force_flag = False):
	# Write image to nifti
	out_img = ni.Nifti1Image(img_data, img_affine)
	if outfname.endswith('.nii.gz'):
		out_img.save(outfname)
	else:
		out_img.save(outfname + '.nii.gz')

def binarize_aseg_data(aseg_data):
	aseg_data[np.where(aseg_data != 0)] = 1
	return aseg_data 

def mask_mni_data(img_data):
	# Load MNI brainmask
	mni_mask = ni.load(MNI_MASK_PATH)
	img_shape = img_data.shape
	if len(img_shape) == 3:
		img_data[np.where(mni_mask == 0)] = 0
		return img_data
	else:
		wrn = 'Warning: MNI mask can only be applied to 3D volume; \
					returning input volume'
		return img_data


