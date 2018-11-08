"""
Main training file

Calls helper functions from utilities
"""
import numpy as np
import sys
from scipy.io import loadmat

from utilities.input import get_params
from pipeline.training import train_with_hic, train_with_mat

if __name__ == '__main__':

	params = get_params()

	rowMap = params['cropMap']['rowMap']
	colMap = params['cropMap']['colMap']

	if not params['usemat']:
		train_with_hic(params)
	else:
		train_with_mat(params)