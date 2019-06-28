import os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from scipy.io import loadmat, savemat
from keras.models import load_model
from utilities.data_processing import hicToMat, trimMat, contactProbabilities, Sigmoid, predictionsToBed

def apply_on_hic(params):
	inputM = hicToMat(params['input_file'], params['juicer_tools_path'],
		tmp_dir=params['dump_dir'],
		prefix='input',
		autoremove=params['autoremove'],
		overwrite=params['overwrite'],
		save_matrix=params['save_matrix']
	)

	print('Trimming sparse, NA, and B4 regions...')
	inputM = trimMat(inputM,params['cropIndices'])
	print('Computing contact probabilities')
	inputM = contactProbabilities(inputM)

	odd_encoder = load_model(params['odd_encoder'])
	odd_clf = load_model(params['odd_classifier'])
	even_encoder = load_model(params['even_encoder'])
	even_clf = load_model(params['even_classifier'])

	odd_enc = Sigmoid(odd_encoder.predict(inputM))
	odd_predictions = odd_clf.predict(odd_enc)
	even_enc = Sigmoid(even_encoder.predict(inputM.T))
	even_predictions = even_clf.predict(even_enc)

	savemat(params['output_path'],{
		'odd_predictions'	:	odd_predictions,
		'even_predictions'	:	even_predictions,
	})

	predictionsToBed(os.path.splitext(params['output_path'])[0] + '.bed', odd_predictions, even_predictions, params['cropMap'])

def apply_on_mat(params):
	inputM = loadmat(params['input_file'])['inter_matrix']

	print('Trimming sparse, NA, and B4 regions...')
	inputM = trimMat(inputM,params['cropIndices'])
	print('Computing contact probabilities')
	inputM = contactProbabilities(inputM)

	odd_encoder = load_model(params['odd_encoder'])
	odd_clf = load_model(params['odd_classifier'])
	even_encoder = load_model(params['even_encoder'])
	even_clf = load_model(params['even_classifier'])

	odd_enc = Sigmoid(odd_encoder.predict(inputM))
	odd_predictions = odd_clf.predict(odd_enc)
	even_enc = Sigmoid(even_encoder.predict(inputM.T))
	even_predictions = even_clf.predict(even_enc)

	savemat(params['output_path'],{
		'odd_predictions'	:	odd_predictions,
		'even_predictions'	:	even_predictions,
	})