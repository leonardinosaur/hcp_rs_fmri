from rs_tools import *
import pandas as pd

def extract_network_bmasks(infname, aseg_paths, outfname):
	ts_data, err_code = read_ts_data(infame)
	if err_code:
		print 'Problem reading time-series volumes...'
		return 1

	ts_df = pd.DataFrame()
	for ind in range(len(aseg_paths)):
		apath = aseg_paths[ind]
		aseg_data, err_code = read_aseg_data(apath)
		if err_code:
			print 'Problem reading aseg volume...'
			return 1
		
		aseg_mask = binarize_aseg_data(aseg_data)
		roi_ts = calc_roi_ts(ts_data, aseg_mask, 1)
		ts_df[ind] = roi_ts_data

	corr_df = ts_df.corr()
	corr_mat = corr_df.values


	return 0




def extract_network_aseg(infame, aseg_path, outfname):
	return 1