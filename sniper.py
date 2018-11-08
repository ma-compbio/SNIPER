"""
Application file

Calls helper functions from utilities
"""
import numpy as np
import sys
from scipy.io import loadmat

from utilities.input import get_application_params
from pipeline.application import apply_on_hic, apply_on_mat

if __name__ == '__main__':

	params = get_application_params()

	if not params['usemat']:
		apply_on_hic(params)
	else:
		apply_on_mat(params)