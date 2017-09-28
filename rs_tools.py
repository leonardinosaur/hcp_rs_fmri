import nibabel as ni
import numpy as np
import os
import random

def read_volume(img_path, dims = 4):

	# Load image
	img = ni.load(imp_path)
	img_data = img.get_data()
	img_shape = img_data.shape
	
	# Check dimensions
	if img_shape != dims:
		wrn = 'Warning: %s has %s dimensions, expected %s. Will proceed with trying to read volume'\
				% (img_path, str(dims))
		print wrn

	# Get image info
	img_aff = img.get_affine()
	img_hdr = img.get_header()

	return img_data, img_aff, img_hdr


def read_ts_data(img_path):
	err_code = 0

	# Should probably change this to accept .mgz files too
	if (not img_path.endswith('.nii.gz')) and (not img_path.endswith('.nii')):
		err = 'Error: time-series volume must be .nii/.nii.gz format'
		print err
		err_code = 1
		return [], err_code

	# Load image
	img = ni.load(imp_path)
	img_data = img.get_data()
	img_shape = img_data.shape

	if img_shape != 3:
		err='Error: time-series volume must be 4D; input volume has %s dimension(s)' % (str(img_shape))
		print err
		err_code = 1

	return img_data, err_code

def read_aseg_data(imp_path):
	err_code = 0
	
	# Should probably change this to accept .mgz files too
	if (not img_path.endswith('.nii.gz')) and (not img_path.endswith('.nii')):
		err = 'Error: time-series volume must be .nii/.nii.gz format'
		print err
		err_code = 1
		return [], err_code

	# Load image
	img = ni.load(imp_path)
	img_data = img.get_data()
	img_shape = img_data.shape

	if img_shape != 3:
		err='Error: aseg volume must be 3D; input has %s dimensions' % (str(img_shape))
		print err
		err_code = 1

	return img_data, err_code



def write_nifti_volume(img_data, img_affine, outfname):
	# Write image to nifti
	out_img = ni.Nifti1Image(img_data, img_affine)
	if outfname.endswith('.nii.gz'):
		out_img.save(outfname)
	else:
		out_img.save(outfname + '.nii.gz')

def write_array(mat, outfname):
	if os.path.exists(outfname):
		randid = generate_random_key()
		rand_outfname = randid + '.npy'
		wrn = 'Warning: file %s already exists. Writing results to %s ' % (outfname, rand_outfname)
		np.save(rand_outfname, mat)
	else:
		# This should probably be a try catch
		np.save(outfname, mat)

def calc_rois_ts(img_data, aseg_data):
	if hasattr(label, '__iter__'):
		roi_ts_vals = {}

		labels = get_aseg_labels(aseg_data)
		for label in labels:
			roi_ts_vals[label] = calc_roi_ts(img_data, aseg_data, label)
		return roi_ts_vals
	else:
		err = 'Value passed into LABEL must be iterable. If you need time series \
					for single ROI, use calc_roi_ts instead.'
		return -4

def calc_roi_ts(img_data, aseg_data, label):
	
	# Might want to add a check to ensure 
	# 	that it is 4D data
	ts_vals = []
	for i in range(img_data.shape[3]):
		tp_data = img_data[:, :, :, i]
		roi_mean = np.mean(tp_data[np.where(aseg_data == label)])
		ts_vals.append(roi_mean)
	
	return ts_vals

def binarize_aseg_data(aseg_data):
	aseg_data[np.where(aseg_data != 0)] = 1
	return aseg_data 


def get_aseg_labels(aseg_data):
	return sorted(list(set(aseg_data.flatten())))

def generate_random_key():
	alpha_num = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
	return ''.join(random.choice(alpha_num) for i in range(16))


# Everything below, isnt done yet

def calc_mean_volume(img_data):
	img_shape = img_data.shape
	if img_shape != 4:
		err = 'Error: image data does not have 4 dimensions'
		print err
		return -4
	mean_vol = img_data.mean(axis = 3)
	return mean_vol, 0