import os
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from scipy.io import loadmat
from utilities.data_processing import hicToMat, trimMat, contactProbabilities, bootstrap, Sigmoid
from pipeline.models import DenoisingAutoencoder, Classifier

from keras.utils import to_categorical

def trainNN(inputM,targetM,params):
	
	odd_labels = loadmat(params['label_file'])['rows'].flatten()
	even_labels = loadmat(params['label_file'])['cols'].flatten()

	print('Training autoencoders...')

	odd_dae_model, odd_encoder, _ = DenoisingAutoencoder(inputM, targetM)
	even_dae_model, even_encoder, _ = DenoisingAutoencoder(inputM.T, targetM.T)

	odd_dae_model.fit(inputM[:7000],targetM[:7000],epochs=10,batch_size=32,
                validation_data=[inputM[7000:],targetM[7000:]])
	even_dae_model.fit(inputM.T[:7000],targetM.T[:7000],epochs=10,batch_size=32,
                validation_data=[inputM.T[7000:],targetM.T[7000:]])

	odd_encodings = Sigmoid(odd_encoder.predict(inputM))
	even_encodings = Sigmoid(even_encoder.predict(inputM.T))

	odd_clf = Classifier(odd_encodings)
	even_clf = Classifier(even_encodings)

	odd_X,odd_y = bootstrap(odd_encodings[:7000],odd_labels[:7000],samplesPerClass=2000)
	even_X,even_y = bootstrap(even_encodings[:7000],even_labels[:7000],samplesPerClass=2000)

	print('Training classifiers...')
	odd_clf.fit(odd_X,to_categorical(odd_y), epochs=25, batch_size=32, verbose=0,
		validation_data=[odd_encodings[7000:],to_categorical(odd_labels[7000:])])
	
	even_clf.fit(even_X,to_categorical(even_y), epochs=25, batch_size=32, verbose=0,
		validation_data=[even_encodings[7000:],to_categorical(even_labels[7000:])])

	odd_dae_model.save(os.path.join(params['dump_dir'],'odd_chrm_autoencoder.h5'))
	odd_encoder.save(os.path.join(params['dump_dir'],'odd_chrm_encoder.h5'))
	odd_clf.save(os.path.join(params['dump_dir'],'odd_chrm_classifier.h5'))

	even_dae_model.save(os.path.join(params['dump_dir'],'even_chrm_autoencoder.h5'))
	even_encoder.save(os.path.join(params['dump_dir'],'even_chrm_encoder.h5'))
	even_clf.save(os.path.join(params['dump_dir'],'even_chrm_classifier.h5'))

def train_with_hic(params):
	print('Constructing input matrix')

	if 'juicer_tools_path' not in params:
		raise Exception('No juicer_tools path specified.')
		sys.exit()

	inputM = hicToMat(params['input_file'],
		params['juicer_tools_path'],
		tmp_dir=params['dump_dir'],
		prefix='input',
		autoremove=params['autoremove'],
		overwrite=params['overwrite'],
		save_matrix=params['save_matrix']
	)

	print('Trimming sparse regions...')
	inputM = trimMat(inputM,params['cropIndices'])
	print('Computing contact probabilities')
	inputM = contactProbabilities(inputM)

	print('Constructing target matrix')

	targetM = hicToMat(params['target_file'],
		params['juicer_tools_path'],
		tmp_dir=params['dump_dir'],
		prefix='target',
		autoremove=params['autoremove'],
		overwrite=params['overwrite'],
		save_matrix=params['save_matrix']
	)

	print('Trimming sparse regions...')
	targetM = trimMat(targetM,params['cropIndices'])
	print('Computing contact probabilities')
	targetM = contactProbabilities(targetM)

	trainNN(inputM, targetM, params)

"""
This function will bypass the need to reconstruct .mat files of the inter-chromosomal Hi-C matrix
from a raw .hic file.

Use train_with_hic when training SNIPER for the first time. Turn on the -sm flag to save the
matrix as a .mat file, which will save the Hi-C matrix to the output directory specified by the
-dd flag.
"""
def train_with_mat(params):
	print ('Using pre-computed .mat files, skipping hic-to-mat')
	inputM = loadmat(params['input_file'])['inter_matrix']
	targetM = loadmat(params['target_file'])['inter_matrix']

	print('Trimming sparse regions from input matrix...')
	inputM = trimMat(inputM,params['cropIndices'])
	print('Computing contact probabilities')
	inputM = contactProbabilities(inputM)

	print('Trimming sparse regions from target matrix...')
	targetM = trimMat(targetM,params['cropIndices'])
	print('Computing contact probabilities')
	targetM = contactProbabilities(targetM)

	trainNN(inputM, targetM, params)