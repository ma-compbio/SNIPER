import sys

from scipy.io import loadmat

def get_params():
	# set defaults

	if len(sys.argv) < 4:
		raise Exception('Must specify input and target .hic or .mat files and a label file')

	params = {
		'usemat' : False,
		'input_file': sys.argv[1],
		'target_file': sys.argv[2],
		'label_file': sys.argv[3],
	}

	if params['input_file'].endswith('.mat'):
		params['usemat'] = True

	"""
	Specify a path to juicer_tools.jar
	"""
	if '-jt' in sys.argv:
		jtIdx = sys.argv.index('-jt') + 1
		params['juicer_tools_path'] = sys.argv[jtIdx]

	"""
	Check if using custom crop folder including cropMap and cropIndices.
	Recommended to set this if not running SNIPER from its root directory.
	"""
	if '-c' in sys.argv:
		cIdx = sys.argv.index('-c') + 1
		try:
			params['cropMap'] = loadmat(os.path.join(sys.argv[cIdx],'cropMap.mat'))
			params['cropIndices'] = loadmat(os.path.join(sys.argv[cIdx],'cropIndices.mat'))
		except:
			raise Exception('No custom crop folder specified')
			sys.exit()
	else:
		params['cropMap'] = loadmat('crop_map/cropMap.mat')
		params['cropIndices'] = loadmat('crop_map/cropIndices.mat')

	"""
	Set dump location for hic text outputs, which are erased after converting
	to a matrix file if -ar is set.
	Strongly recommended if SNIPER is installed on a solid state drive.
	"""
	params['dump_dir'] = '.'

	if '-dd' in sys.argv:
		ddIdx = sys.argv.index('-dd') + 1
		try:
			params['dump_dir'] = sys.argv[ddIdx]
		except:
			raise Exception('No dump directory specified')
			sys.exit()

	"""
	Set -sm to save matrix to .mat file to a specified path
	"""
	params['save_matrix'] = False

	if '-sm' in sys.argv:
		params['save_matrix'] = True

	"""Set -ar to autoremove hic text files"""
	params['autoremove'] = False
	if '-ar' in sys.argv:
		params['autoremove'] = True

	"""Set -ow to overwrite existing hic text files"""
	params['overwrite'] = False
	if '-ow' in sys.argv:
		params['overwrite'] = True

	return params

def get_application_params():
	params = {
		'usemat' : False,
		'input_file': sys.argv[1],
		'output_path': sys.argv[2],
		'odd_encoder': sys.argv[3],
		'odd_classifier': sys.argv[4],
		'even_encoder': sys.argv[5],
		'even_classifier': sys.argv[6],
	}

	if params['input_file'].endswith('.mat'):
		params['usemat'] = True

	params['dump_dir'] = '.'

	if '-dd' in sys.argv:
		ddIdx = sys.argv.index('-dd') + 1
		try:
			params['dump_dir'] = sys.argv[ddIdx]
		except:
			raise Exception('No dump directory specified')
			sys.exit()

	params['save_matrix'] = False

	"""	Set -sm to save matrix to .mat file to a specified path	"""
	if '-sm' in sys.argv:
		params['save_matrix'] = True

	"""Set -ar to autoremove hic text files"""
	params['autoremove'] = False
	if '-ar' in sys.argv:
		params['autoremove'] = True

	"""Set -ow to overwrite existing hic text files"""
	params['overwrite'] = False
	if '-ow' in sys.argv:
		params['overwrite'] = True

	if '-c' in sys.argv:
		cIdx = sys.argv.index('-c') + 1
		try:
			params['cropMap'] = loadmat(os.path.join(sys.argv[cIdx],'cropMap.mat'))
			params['cropIndices'] = loadmat(os.path.join(sys.argv[cIdx],'cropIndices.mat'))
		except:
			raise Exception('No custom crop folder specified')
			sys.exit()
	else:
		params['cropMap'] = loadmat('crop_map/cropMap.mat')
		params['cropIndices'] = loadmat('crop_map/cropIndices.mat')

	"""
	Specify a path to juicer_tools.jar
	"""
	if '-jt' in sys.argv:
		jtIdx = sys.argv.index('-jt') + 1
		params['juicer_tools_path'] = sys.argv[jtIdx]

	return params